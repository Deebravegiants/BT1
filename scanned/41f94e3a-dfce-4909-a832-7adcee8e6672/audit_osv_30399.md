# [H] DataEase has a forged JWT token vulnerability

## Summary
Severity: High
Advisory: CVE-2024-52295
Aliases: GHSA-45v9-gfcv-xcq6
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2024-11-13
Source: https://osv.dev/vulnerability/CVE-2024-52295
Type: osv

## Details
DataEase is an open source data visualization analysis tool. Prior to 2.10.2, DataEase allows attackers to forge jwt and take over services. The JWT secret is hardcoded in the code, and the UID and OID are hardcoded. The vulnerability has been fixed in v2.10.2.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/52xxx/CVE-2024-52295.json
- https://github.com/dataease/dataease/security/advisories/GHSA-45v9-gfcv-xcq6
- https://nvd.nist.gov/vuln/detail/CVE-2024-52295
- https://github.com/dataease/dataease/commit/e755248d59543bcd668ace495f293ff735fa82e9
