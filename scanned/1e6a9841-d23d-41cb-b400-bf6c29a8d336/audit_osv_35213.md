# [M] free5GC has Improper Input Validation in UDM, Leading to Information Exposure

## Summary
Severity: Medium
Advisory: CVE-2025-69251
Aliases: GHSA-pwxh-4qh4-hgpq
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N/E:U)
Published: 2026-02-23
Source: https://osv.dev/vulnerability/CVE-2025-69251
Type: osv

## Details
free5gc UDM provides Unified Data Management (UDM) for free5GC, an open-source project for 5th generation (5G) mobile core networks. In versions up to and including 1.4.1, remote attackers can inject control characters (e.g., %00) into the ueId parameter, triggering internal URL parsing errors (net/url: invalid control character). This exposes system implementation details and can aid in service fingerprinting. All deployments of free5GC using the UDM Nudm_UECM service may be affected. free5gc/udm pull request 76 contains a fix for the issue. No direct workaround is available at the application level. Applying the official patch is recommended.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/69xxx/CVE-2025-69251.json
- https://github.com/free5gc/free5gc/security/advisories/GHSA-pwxh-4qh4-hgpq
- https://nvd.nist.gov/vuln/detail/CVE-2025-69251
- https://github.com/free5gc/free5gc/issues/751
- https://github.com/free5gc/free5gc/issues/76
- https://github.com/free5gc/udm/commit/504b14458d156558b3c0ade7107b86b3d5e72998
