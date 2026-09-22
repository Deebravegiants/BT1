# [M] OpenEMR 7.0.1 Authentication Brute Force Mitigation Bypass

## Summary
Severity: Medium
Advisory: CVE-2023-54347
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-05-05
Source: https://osv.dev/vulnerability/CVE-2023-54347
Type: osv

## Details
OpenEMR 7.0.1 contains an authentication brute force vulnerability that allows attackers to bypass rate limiting protections by sending repeated login attempts to the main login endpoint. Attackers can submit POST requests with authUser and clearPass parameters to systematically test username and password combinations without account lockout restrictions.

## References
- https://github.com/openemr/openemr/archive/refs/tags/v7_0_1.tar.gz
- https://www.open-emr.org/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/54xxx/CVE-2023-54347.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-54347
- https://www.vulncheck.com/advisories/openemr-authentication-brute-force-mitigation-bypass
- https://www.exploit-db.com/exploits/51413
