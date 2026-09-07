# [M] Session fixation

## Summary
Severity: Medium
Advisory: GHSA-v2wf-c3j6-wpvw
CVE: CVE-2020-5205
CWE: CWE-384
Ecosystem: Hex
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:C/C:H/I:L/A:N (CVSS_V3)
Published: 2022-04-12
Source: https://github.com/advisories/GHSA-v2wf-c3j6-wpvw
Type: github-advisory

## Affected
- Hex: `pow` — affected >=0 <1.0.16

## Details
### Impact

The use of `Plug.Session` in `Pow.Plug.Session` is susceptible to session fixation attacks if a persistent session store is used for `Plug.Session`, such as Redis or a database. Cookie store, which is used in most Phoenix apps, doesn't have this vulnerability.

### Workarounds

Call `Plug.Conn.configure_session(conn, renew: true)` periodically and after privilege change. A custom authorization plug can be written where the `create/3` method should return the `conn` only after `Plug.Conn.configure_session/2` have been called on it.

### References
https://github.com/danschultzer/pow/commit/578ffd3d8bb8e8a26077b644222186b108da474f  
https://www.owasp.org/index.php/Session_fixation

## References
- https://github.com/danschultzer/pow/security/advisories/GHSA-v2wf-c3j6-wpvw
- https://nvd.nist.gov/vuln/detail/CVE-2020-5205
- https://github.com/danschultzer/pow/commit/578ffd3d8bb8e8a26077b644222186b108da474f
- https://github.com/danschultzer/pow
- https://github.com/danschultzer/pow/blob/master/CHANGELOG.md#v1016-2020-01-07
