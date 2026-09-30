# [M] langgraph-api: Incomplete assistant authorization in LangGraph Server run creation

## Summary
Severity: Medium
Advisory: GHSA-jfj5-wrj9-63x4
CVE: CVE-2026-55236
CWE: CWE-285
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2026-08-19
Source: https://github.com/advisories/GHSA-jfj5-wrj9-63x4
Type: github-advisory

## Affected
- PyPI: `langgraph-api` — affected >=0 <0.10.0

## Details
## Summary

In affected versions of `langgraph-api` (the LangGraph Server runtime), the run-creation path authorized the assistant attached to a run using a different authorization event than the rest of the assistant-handling code paths. Direct assistant reads and cron creation dispatch the `assistants.read` authorization event; run creation dispatched `assistants.search` with an incomplete value. In deployments whose custom authorization handlers register only an `assistants.read` handler (without an `assistants.search` handler and without a global fallback handler), no handler was consulted on the run-creation path, the returned filter set was empty, and the owner constraint was omitted from the resulting query.

As a result, in those deployments a request to create a run could reference a private assistant owned by another user, even where direct assistant reads, assistant search, and cron creation against that assistant were correctly denied. The run-creation response merged the referenced assistant's `metadata`, `config`, and `context` into fields returned to the requesting user. These fields can carry sensitive configuration; the runtime encrypts them at rest for that reason.

We have no evidence of this behavior occurring in the wild.

## Affected users / systems

You may be affected if you:

- run `langgraph-api` (the LangGraph Server / Agent Server runtime, including via the LangGraph Platform Helm chart), and
- use custom authorization handlers that gate assistant access through an `assistants.read` or `assistants.search` handler rather than a global handler covering all assistant events.

Deployments without custom authorization handlers, or whose handlers apply an equivalent owner filter across all assistant events (for example through a global handler), are not affected.

## Impact

- Confidentiality: exposure of another user's private assistant `metadata`, `config`, and `context` through the run-creation response. These fields can contain sensitive configuration.
- Integrity: creation of a run associated with another user's private assistant, beyond the requesting user's authorization scope; the run is then carried out using that assistant's configuration.

## Patches / mitigation

Run creation, and the parallel cron-creation path, now dispatch the `assistants.read` authorization event in both the in-memory and gRPC/Postgres runtimes, matching direct assistant reads. Client-supplied run and cron metadata is no longer forwarded into that authorization event, so handlers receive a consistent value shape and determine access by returning an owner filter that is applied server-side. Fixed in `langgraph-api` 0.10.0.

This is a behavioral change for deployments with custom authorization handlers:

- Handlers that gated assistant access only through `assistants.search` during run creation are no longer consulted on that path; provide an equivalent `assistants.read` handler that returns the same owner filter.
- The metadata field on the `assistants.read` event during run and cron creation is no longer populated; handlers that read or stamped it should move that logic into the run/cron create handlers.

## Operational guidance

- Register an `assistants.read` handler (or a global handler covering it) that returns an owner-style filter, and confirm parity across the assistant read, search, and run/cron creation paths.
- Upgrade to a release containing this change.

## References
- https://github.com/langchain-ai/helm/security/advisories/GHSA-jfj5-wrj9-63x4
- https://github.com/langchain-ai/helm
