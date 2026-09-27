# [H] LangChain MongoDB has NoSQL Operator Injection in MongoDBSaver.list() leading to cross-tenant data exposure

## Summary
Severity: High
Advisory: GHSA-533j-2v4q-mw5h
CVE: CVE-2026-55253
CWE: CWE-943
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2026-08-20
Source: https://github.com/advisories/GHSA-533j-2v4q-mw5h
Type: github-advisory

## Affected
- PyPI: `langgraph-checkpoint-mongodb` — affected >=0 <0.3.0
- PyPI: `langgraph-store-mongodb` — affected >=0 <0.4.0

## Details
# Executive Summary

A NoSQL injection issue exists in the langgraph-checkpoint-mongodb and
langgraph-store-mongodb libraries. MongoDBSaver.list() and MongoDBStore.search() methods
accept a filter parameter that is incorporated into MongoDB queries without sufficient validation.
Because MongoDB query operator keys (those prefixed with $) are not rejected during filter
construction, a caller with control of the filter input can embed MongoDB query operators
directly into the query.

---

## CVSS Details

### CVSS 4.0

| Field | Value |
|---|---|
| **CVSS Version** | 4.0 |
| **Vector String** | `CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:N/VA:N/SC:H/SI:N/SA:N` |
| **Base Score** | **7.1 (High)** |

| Metric | Value | Rationale |
|---|---|---|
| Attack Vector (AV) | Network | Triggerable remotely via API |
| Attack Complexity (AC) | Low | No special conditions required |
| Attack Requirements (AT) | None | No prerequisite deployment or execution conditions |
| Privileges Required (PR) | Low | Authenticated caller of the checkpoint/store API |
| User Interaction (UI) | None | No user action required |
| Vulnerable System Confidentiality (VC) | None | No direct impact on the vulnerable component itself |
| Vulnerable System Integrity (VI) | None | Read-only access |
| Vulnerable System Availability (VA) | None | No service disruption |
| Subsequent System Confidentiality (SC) | High | Full access to other tenants' checkpoint data |
| Subsequent System Integrity (SI) | None | No write or modification capability |
| Subsequent System Availability (SA) | None | No service disruption to downstream systems |

### CVSS 3.1

| Field | Value |
|---|---|
| **CVSS Version** | 3.1 |
| **Vector String** | `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N` |
| **Base Score** | **7.7 (High)** |

| Metric | Value | Rationale |
|---|---|---|
| Attack Vector | Network | Triggerable remotely via API |
| Attack Complexity | Low | No special conditions required |
| Privileges Required | Low | Authenticated caller of the checkpoint/store API |
| User Interaction | None | No user action required |
| Scope | Changed | Impact crosses tenant boundaries |
| Confidentiality | High | Full access to other tenants' checkpoint data |
| Integrity | None | Read-only access |
| Availability | None | No service disruption |
---
## Affected Packages
| Package | Distribution | Affected Methods | Affected Versions |
|---|---|---|---|
| `langgraph-checkpoint-mongodb` | PyPI | `MongoDBSaver.list()`, `MongoDBSaver.alist()` | < 0.3.0 |
| `langgraph-store-mongodb` | PyPI | `MongoDBStore.search()` | < 0.4.0 |
---
## Advisory FAQ
### How do I know if I am affected?

You are likely affected if **all** of the following are true:
1. Your application uses `langgraph-checkpoint-mongodb` or `langgraph-store-mongodb`.
2. Your application calls `MongoDBSaver.list()`, `MongoDBSaver.alist()`, or
`MongoDBStore.search()` with a `filter` argument.
3. Any part of that `filter` argument is derived from user-controlled input — for example, HTTP
query parameters, request body fields, or agent tool arguments.
4. You operate in a multi-tenant context where the `filter` is used to enforce per-user or
per-tenant data isolation.

If the `filter` argument is constructed entirely from trusted, server-side values, the practical risk is
lower, but upgrading is still recommended.

### How do I fix the issue?

**Upgrade** to the version of `langgraph-checkpoint-mongodb` and `langgraph-store-mongodb`.
If you cannot upgrade immediately, apply the following mitigation: in your application code,
before passing any user-controlled input to the `filter` parameter, remove or escape MongoDB
Query metacharacters such as “$”.

---

## Acknowledgements
Thanks to Kenichi Kawaguchi for responsibly disclosing this issue via the GitHub Security
Advisory program on the langchain-mongodb repository.

---

## Revisions

| Date | Description |
|---|---|
| 2026-06-05 | Initial advisory published |

## References
- https://github.com/langchain-ai/langchain-mongodb/security/advisories/GHSA-533j-2v4q-mw5h
- https://github.com/langchain-ai/langchain-mongodb
- https://github.com/langchain-ai/langchain-mongodb/releases/tag/libs%2Flanggraph-checkpoint-mongodb%2Fv0.4.0
- https://github.com/langchain-ai/langchain-mongodb/releases/tag/libs%2Flanggraph-store-mongodb%2Fv0.3.0
