# URL Shortener — Agent Development Contract

## 1. Mission

This repository is a production-oriented URL shortener.

Theis currently supports the core URL-shortening workflow and will be incrementally extended with additional capabilities.

The goal is to build the system as if it will eventually operate as a real distributed production service.

Coding Agents must prioritize:

1. Correctness
2. Simplicity
3. Testability
4. Clear separation of concerns
5. Reliability
6. Observability
7. Backward compatibility
8. Incremental evolution

Do not introduce complexity unless it solves a clearly identified problem.

---

# 2. Technology Constraints

The project uses:

* Python
* FastAPI
* Pydantic
* pytest for testing

Do not replace the existing framework or introduce a new framework without explicit approval.

Do not introduce a new database, queue, cache, ORM, cloud service, or infrastructure dependency merely because it is common in production systems.

Every new infrastructure dependency must have a clear justification.

---

# 3. Existing Architecture

The current application follows this basic separation:

```text
HTTP Request
     |
     v
main.py
     |
     v
schemas.py
     |
     v
services.py
     |
     v
repository.py
     |
     v
models.py
     |
     v
in-memory Data storage
```

Responsibilities:

### main.py

HTTP/API layer.

Responsible for:

* FastAPI application
* Routes
* HTTP status codes
* Request/response handling
* Dependency injection

Must NOT contain:

* Business logic
* Database queries
* URL-generation algorithms
* Complex validation logic

---

### schemas.py

API contracts.

Responsible for:

* Request schemas
* Response schemas
* API validation
* Serialization

Schemas should represent the API contract, not the database schema.

---

### services.py

Business logic.

Responsible for:

* URL shortening logic
* TTL decisions
* Expiration logic
* Click tracking logic
* Business-level validation
* Coordination between repositories

Services should not depend on FastAPI-specific objects.

---

### repository.py

Persistence abstraction.

Responsible for:

* Reading/writing persistent data
* Database queries
* Persistence-specific operations

Business rules should NOT live here.

The repository should expose meaningful operations rather than leaking raw database implementation details into services.

---

### models.py

Persistence/domain models, when DB integration is completed. 

Responsible for:

* Database entities
* Persistence representation
* Model-level constraints where appropriate

Do not put API-specific request/response models here.

---

# 4. Architectural Rules

Maintain the following dependency direction:

```text
API
 |
 v
Service
 |
 v
Repository
 |
 v
Database
```

Lower layers must not depend on higher layers.

For example:

GOOD:

```text
main.py -> services.py -> repository.py
```

BAD:

```text
repository.py -> services.py
repository.py -> main.py
```

BAD:

```text
services.py -> FastAPI Request
```

Keep business logic framework-independent wherever practical.

---

# 5. Core Domain

A shortened URL currently has the conceptual form:

```text
ShortURL
----------------
id
short_code
original_url
created_at
expires_at
click_count
```

The exact representation may evolve.

Do not change the public API or persistence model without considering backward compatibility.

---

# 6. URL Creation

The system must support:

```text
Original URL
      |
      v
Generate unique short code
      |
      v
Persist mapping
      |
      v
Return shortened URL
```

Short codes must be unique.

Never assume generated identifiers are collision-free unless uniqueness is guaranteed by the underlying mechanism.

Database uniqueness must be treated as an important correctness boundary.

---

# 7. TTL

URLs may have configurable TTL.

The system must distinguish between:

```text
created_at
expires_at
```

Expiration should be evaluated using server-side time.

Do not rely on client-provided current timestamps for expiration decisions.

Do not silently change the meaning of an existing TTL API.

If TTL behavior changes, update tests and documentation.

---

# 8. Click Tracking

Every successful redirect should increment the click count.

Do not increment the click count when:

* the short code does not exist
* the URL has expired
* the request fails before a successful redirect

Click counting must be implemented in a way that does not introduce obvious lost-update bugs under concurrent requests.

If concurrency semantics are changed, add a test demonstrating the intended behavior.

---

# 9. API Design

API behavior must be explicit.

For every endpoint define:

* HTTP method
* Path
* Request schema
* Response schema
* Success status
* Failure status
* Error format

Do not casually change existing endpoint behavior.

Before modifying an existing endpoint:

1. Inspect current implementation.
2. Inspect existing tests.
3. Identify backward-compatibility implications.
4. Implement the smallest safe change.
5. Update/add tests.

---

# 10. Testing Rules

Every new feature must include tests.

At minimum consider:

### Happy path

```text
valid input -> expected result
```

### Invalid input

```text
invalid input -> expected validation/error
```

### Boundary conditions

Examples:

* TTL = 0
* very large TTL
* expired URL
* missing URL
* duplicate short code
* malformed URL

### Concurrency

For operations involving counters, uniqueness, or race conditions, consider concurrent execution.

Do not claim concurrency safety without testing or explaining the underlying guarantee.

---

# 11. Agent Workflow

Before modifying code:

1. Inspect the repository.
2. Read AGENTS.md.
3. Read README.md.
4. Read ARCHITECTURE.md (if present)
5. Inspect relevant implementation.
6. Inspect relevant test cases.
7. Explain the proposed change.
8. Identify affected files.
9. Implement the smallest coherent change.
10. Run tests.
11. Fix failures.
12. Re-run tests.
13. Summarize changes.

Do not rewrite unrelated code.

---

# 12. Minimal Change Principle

Prefer:

```text
small change
+
focused test
+
clear explanation
```

over:

```text
large refactor
+
new abstractions
+
new dependencies
```

Do not refactor unrelated code while implementing a feature.

If a refactor is genuinely required, explain why before doing it.

---

# 13. Dependency Rules

Before adding a dependency, determine whether the standard library or an existing dependency can solve the problem.

For every new dependency:

* explain why it is needed
* explain alternatives considered
* verify that it does not duplicate existing functionality

Do not add dependencies silently.

---

# 14. Database Rules

Database correctness is more important than application-level assumptions.

Use database constraints for invariants such as:

* unique short codes
* required fields
* appropriate indexes

Application checks should not be considered sufficient protection against race conditions.

Example:

BAD:

```python
if not repository.exists(short_code):
    repository.create(short_code)
```

This can race under concurrent requests.

Prefer a database uniqueness constraint and handle the resulting conflict correctly.

---

# 15. Time Handling

Use timezone-aware timestamps.

Avoid scattered calls to:

```python
datetime.now()
```

Prefer a consistent time abstraction when time-dependent behavior becomes significant.

Time-dependent logic should be testable.

---

# 16. Error Handling

Do not use broad exception swallowing:

```python
try:
    ...
except Exception:
    pass
```

Do not hide failures.

Errors should be:

* handled intentionally
* converted into appropriate API responses
* logged when appropriate

Never expose internal stack traces or sensitive implementation details through API responses.

---

# 17. Logging

Use structured, meaningful logs where appropriate.

Never log:

* secrets
* credentials
* authorization tokens
* sensitive user information

Avoid excessive logging inside hot paths.

---

# 18. Performance

Do not prematurely optimize.

However, identify obvious scalability problems.

Examples:

* unnecessary database queries
* N+1 queries
* unbounded in-memory structures
* synchronous blocking work in async request paths
* missing indexes
* unnecessary serialization/deserialization

When optimizing, provide evidence or reasoning for the optimization.

---

# 19. Security

Treat all user-provided URLs and request parameters as untrusted input.

Consider:

* malformed URLs
* extremely long URLs
* abuse of URL creation
* open redirect implications
* rate limiting
* resource exhaustion
* malicious payloads

Do not introduce security-sensitive behavior without documenting the threat model.

---

# 20. Observability

As the system evolves, maintain visibility into:

* request latency
* request count
* errors
* redirect count
* URL creation rate
* database latency
* cache behavior where applicable

Metrics should be introduced when they provide meaningful operational value.

---

# 21. Distributed-System Evolution

When introducing:

* Redis
* Kafka
* message queues
* distributed ID generation
* caching
* multiple service instances
* background workers

the agent must explicitly discuss:

* consistency
* failure modes
* retries
* idempotency
* ordering
* concurrency
* data loss
* recovery

Do not add distributed infrastructure merely to make the architecture look more "production-like."

---

# 22. No Fake Production Claims

Do not claim that a feature is:

* highly available
* horizontally scalable
* fault tolerant
* exactly once
* strongly consistent
* concurrency safe

unless the implementation actually provides the required guarantees.

Explain the actual guarantee.

---

# 23. Documentation

Whenever behavior changes, update the relevant documentation.

Important architectural decisions should be documented in:

```text
ARCHITECTURE.md
```

Do not allow the documentation and implementation to drift.

---

# 24. Definition of Done

A feature is NOT complete merely because the code compiles.

A feature is complete when:

* implementation exists
* tests exist
* existing tests still pass
* API behavior is documented
* failure cases are considered
* concurrency implications are considered where relevant
* observability implications are considered where relevant
* no unnecessary dependencies were added
* no unrelated code was changed

---

# 25. Agent Communication

Before implementing a non-trivial change, provide:

### Understanding

What problem is being solved?

### Design

What approach will be used?

### Files

Which files will change?

### Risks

What could go wrong?

### Tests

How will correctness be verified?

After implementation provide:

### Changes

What changed?

### Tests

What was run?

### Result

What passed/failed?

### Follow-ups

What remains intentionally out of scope?

---

# 26. Absolute Don'ts

Never:

* rewrite the entire repository unnecessarily
* delete tests to make tests pass
* weaken assertions to make tests pass
* disable lint/type checking to hide problems
* introduce dependencies without justification
* put business logic in API routes
* put business logic in repositories
* swallow exceptions
* hard-code secrets
* commit credentials
* silently change public API behavior
* silently change database semantics
* optimize without understanding the bottleneck
* claim guarantees the system does not provide
* modify unrelated files
* generate large abstractions for trivial problems

---

# 27. Priority Order

When principles conflict, use this order:

1. Correctness
2. Security
3. Data integrity
4. Reliability
5. Testability
6. Simplicity
7. Performance
8. Developer convenience

Do not sacrifice correctness for elegance.
