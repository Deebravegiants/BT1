# [H] Undertow vulnerable to Dos via Large AJP request

## Summary
Severity: High
Advisory: GHSA-95rf-557x-44g5
CVE: CVE-2022-2053
CWE: CWE-400
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-08-06
Source: https://github.com/advisories/GHSA-95rf-557x-44g5
Type: github-advisory

## Affected
- Maven: `io.undertow:undertow-core` — affected >=0 <2.2.19.Final
- Maven: `io.undertow:undertow-core` — affected >=2.3.0.Alpha1 <2.3.0.Alpha2

## Details
When a POST request comes through AJP and the request exceeds the max-post-size limit (maxEntitySize), Undertow's AjpServerRequestConduit implementation closes a connection without sending any response to the client/proxy. This behavior results in that a front-end proxy marking the backend worker (application server) as an error state and not forward requests to the worker for a while. In mod_cluster, this continues until the next STATUS request (10 seconds intervals) from the application server updates the server state. So, in the worst case, it can result in "All workers are in error state" and mod_cluster responds "503 Service Unavailable" for a while (up to 10 seconds). In mod_proxy_balancer, it does not forward requests to the worker until the "retry" timeout passes. However, luckily, mod_proxy_balancer has "forcerecovery" setting (On by default; this parameter can force the immediate recovery of all workers without considering the retry parameter of the workers if all workers of a balancer are in error state.). So, unlike mod_cluster, mod_proxy_balancer does not result in responding "503 Service Unavailable". An attacker could use this behavior to send a malicious request and trigger server errors, resulting in DoS (denial of service). This flaw was fixed in Undertow 2.2.19.Final, Undertow 2.3.0.Alpha2.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-2053
- https://github.com/undertow-io/undertow/pull/1350
- https://bugzilla.redhat.com/show_bug.cgi?id=2095862&comment#0
- https://github.com/undertow-io/undertow
- https://issues.redhat.com/browse/UNDERTOW-2133
