# [C] Bastillion Authentication Bypass via Path-Prefix Routing Mismatch

## Summary
Severity: Critical
Advisory: CVE-2026-75627
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-18
Source: https://osv.dev/vulnerability/CVE-2026-75627
Type: osv

## Details
Bastillion fails to properly validate request URI paths in its controller dispatcher, allowing unauthenticated attackers to bypass authentication filters by prefixing requests with arbitrary path segments. Attackers can access administrative controllers to read user listings, create manager accounts, and register managed systems, gaining control over SSH access to the managed fleet.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/75xxx/CVE-2026-75627.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-75627
- https://www.vulncheck.com/advisories/bastillion-authentication-bypass-via-path-prefix-routing-mismatch
- https://github.com/bastillion-io/Bastillion/issues/669
- https://github.com/bastillion-io/Bastillion/commit/d759fb686a1a097b1b026e286fd9b20e5ba349c8
- https://github.com/bastillion-io/Bastillion
- https://github.com/bastillion-io/Bastillion/blob/master/src/main/java/loophole/mvc/base/BaseKontroller.java
