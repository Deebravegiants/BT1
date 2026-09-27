# [M] OpenBao leaks HTTPRawBody in Audit Logs

## Summary
Severity: Medium
Advisory: GHSA-ghfh-fmx4-26h8
CVE: CVE-2025-62513
CWE: CWE-532
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:H/UI:P/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-10-22
Source: https://github.com/advisories/GHSA-ghfh-fmx4-26h8
Type: github-advisory

## Affected
- Go: `github.com/openbao/openbao` — affected >=0.0.0-20241114205727-b1235e585db7 <0.0.0-20251022165510-cc2c476bac66

## Details
### Impact

OpenBao's audit log experienced a regression wherein raw HTTP bodies used by few endpoints were not correctly redacted (HMAC'd).  This impacted the following subsystems:

 - When using the ACME functionality of PKI, this would result in short-lived ACME verification challenge codes being leaked in the audit logs.
 - When using the OIDC issuer functionality of the identity subsystem, auth and token response codes along with claims could be leaked in the audit logs.

Third-party plugins may be affected.

### Patches

OpenBao v2.4.2 will patch this issue.

### Workarounds

If users do not use the above functionality, they are not impacted. ACME verification codes are not usable after verification or challenge expiry so are of limited long-term use.

## References
- https://github.com/openbao/openbao/security/advisories/GHSA-ghfh-fmx4-26h8
- https://nvd.nist.gov/vuln/detail/CVE-2025-62513
- https://github.com/openbao/openbao/commit/cc2c476bac66e1d94776c2629793daec3af625f8
- https://github.com/openbao/openbao
