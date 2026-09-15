# [M] dbt allows Binding to an Unrestricted IP Address via socketsocket

## Summary
Severity: Medium
Advisory: GHSA-pmrx-695r-4349
CVE: CVE-2024-36105
CWE: CWE-1327
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2024-05-28
Source: https://github.com/advisories/GHSA-pmrx-695r-4349
Type: github-advisory

## Affected
- PyPI: `dbt-core` — affected >=0 <1.6.15
- PyPI: `dbt-core` — affected >=1.7.0 <1.7.15
- PyPI: `dbt-core` — affected >=1.8.0 <1.8.1

## Details
### Summary

Binding to `INADDR_ANY (0.0.0.0)` or `IN6ADDR_ANY (::)` exposes an application on all network interfaces, increasing the risk of unauthorized access.

While doing some static analysis and code inspection, I found the following code binding a socket to `INADDR_ANY` by passing `""` as the address. This effectively binds to any network interface on the local system, not just localhost (127.0.0.1). 

### Details

As stated in the Python docs, a special form for address is accepted instead of a host address: `''` represents `INADDR_ANY`, equivalent to `"0.0.0.0"`. On systems with IPv6, '' represents `IN6ADDR_ANY`, which is equivalent to `"::"`. 

https://github.com/dbt-labs/dbt-core/blob/main/core/dbt/task/docs/serve.py#L23C38-L23C39

The text around this code also imply the intention is to host docs only on localhost.

### PoC

To recreate, run the docs ServeTask.run() to stand up the HTTP server.  Then run `netstat` to see what addresses this process is bound.

### Impact

A user who serves docs on an unsecured public network, may unknowingly be hosting an unsecured (http) web site for any remote user/system to access on the same network.

Further references:
https://docs.python.org/3/library/socket.html#socket-families
https://docs.securesauce.dev/rules/PY030
https://cwe.mitre.org/data/definitions/1327.html

### Patches
The issue has has been mitigated in [dbt-core v1.6.15](https://github.com/dbt-labs/dbt-core/releases/tag/v1.6.15), [dbt-core v1.7.15](https://github.com/dbt-labs/dbt-core/releases/tag/v1.7.15), and [dbt-core v1.8.1](https://github.com/dbt-labs/dbt-core/releases/tag/v1.8.1) by binding to localhost explicitly by default in `dbt docs serve` (https://github.com/dbt-labs/dbt-core/issues/10209).

## References
- https://github.com/dbt-labs/dbt-core/security/advisories/GHSA-pmrx-695r-4349
- https://nvd.nist.gov/vuln/detail/CVE-2024-36105
- https://github.com/dbt-labs/dbt-core/issues/10209
- https://github.com/dbt-labs/dbt-core/pull/10208
- https://github.com/dbt-labs/dbt-core/commit/0c08d7a19ad1740be3cb0b2e6d9d64f6537176f7
- https://cwe.mitre.org/data/definitions/1327.html
- https://docs.python.org/3/library/socket.html#socket-families
- https://docs.securesauce.dev/rules/PY030
- https://github.com/dbt-labs/dbt-core
- https://github.com/dbt-labs/dbt-core/blob/main/core/dbt/task/docs/serve.py#L23C38-L23C39
- https://github.com/dbt-labs/dbt-core/releases/tag/v1.6.15
- https://github.com/dbt-labs/dbt-core/releases/tag/v1.7.15
- https://github.com/dbt-labs/dbt-core/releases/tag/v1.8.1
