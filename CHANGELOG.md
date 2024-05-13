# CHANGELOG

## v0.1.1

### Code Changes

- Remove code for automatic evaluation and filtering of jobs:
  * Remove `ReviewCog`, `StoreJobFunctor`, and unused functors
  * Remove `utils` module, old notebooks, and `helpers` module
- Implement Pydantic for `Job`
- Convert `FeedParser` and `NewJobsHandler` into dedicated function

---

## v0.1.0

### Code Changes

- Convert bot functionality to be a simple RSS notifier. This required modifying `NewJobsHandler.__call__` to _not_ filter jobs
- Add Dockerfile for deployment to Digital Ocean