# [M] langgraph-api: Relative webhook targets in LangGraph Server can reach in-process routes without authentication

## Summary
Severity: Medium
Advisory: GHSA-2c9q-c2q9-qgqv
CVE: CVE-2026-55235
CWE: CWE-287
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:N/I:H/A:L (CVSS_V3)
Published: 2026-08-19
Source: https://github.com/advisories/GHSA-2c9q-c2q9-qgqv
Type: github-advisory

## Affected
- PyPI: `langgraph-api` — affected >=0 <0.10.0

## Details
## Summary

In affected versions of `langgraph-api` (the LangGraph Server runtime), a run or cron could be created with a relative webhook target. When the server later delivers such a webhook, it routes the request back into the same application through an in-process loopback transport that the authentication middleware treats as internal and does not authenticate. As a result, a relative webhook target could reach the server's own routes that operate on threads and runs without the authentication context that applies to ordinary external requests.

In deployments that scope threads and runs by owner, this could allow a request associated with one user to reach routes operating on another user's thread, resulting in creation of a run on (or modification of the state of) a thread owned by another user, even where the corresponding direct external requests were correctly denied. Limited metadata from the targeted thread may be incorporated into the created run record.

We have no evidence of this behavior occurring in the wild.

## Affected users / systems

You may be affected if you:

- run `langgraph-api` (the LangGraph Server / Agent Server runtime, including via the LangGraph Platform Helm chart),
- allow runs or crons to specify webhook targets, and
- rely on per-user authorization to separate threads and runs between users.

## Impact

- Integrity: creation of a run on, or modification of the state of, a thread owned by another user, beyond the requesting user's authorization scope.
- Confidentiality: limited exposure of another user's thread metadata, incorporated into the created run record.

## Patches / mitigation

The webhook URL policy now denies loopback delivery by default: the `webhooks.url.disable_loopback` policy defaults to enabled. This covers relative webhook targets routed through the in-process transport, as well as localhost-style hostnames, loopback address ranges, and hostnames that resolve into the loopback range. Deployments that legitimately deliver webhooks to a route hosted on the same process can opt back in by setting `webhooks.url.disable_loopback: false` in `langgraph.json` (or the equivalent `LANGGRAPH_WEBHOOKS` configuration); do so only when you control the routes those webhooks reach, as they are delivered without authentication. Fixed in `langgraph-api` 0.10.0.

## Operational guidance

- Upgrade to a release containing this change and keep loopback webhook delivery disabled unless required.
- If loopback delivery is enabled, restrict it to routes you control and apply authorization within those routes.

## References
- https://github.com/langchain-ai/helm/security/advisories/GHSA-2c9q-c2q9-qgqv
- https://github.com/langchain-ai/helm
