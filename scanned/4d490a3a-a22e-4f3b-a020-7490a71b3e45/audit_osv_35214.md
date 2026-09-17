# [M] free5GC has Null Pointer Dereference in UDM, Leading to Service Panic

## Summary
Severity: Medium
Advisory: CVE-2025-69252
Aliases: GHSA-v8cv-qvf6-9rpm
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N/E:U)
Published: 2026-02-23
Source: https://osv.dev/vulnerability/CVE-2025-69252
Type: osv

## Details
free5gc UDM provides Unified Data Management (UDM) for free5GC, an open-source project for 5th generation (5G) mobile core networks. Versions up to and including 1.4.1 have a NULL Pointer Dereference vulnerability. Remote unauthenticated attackers can trigger a service panic (Denial of Service) by sending a crafted PUT request with an unexpected ueId, crashing the UDM service. All deployments of free5GC using the UDM component may be affected. free5gc/udm pull request 76 contains a fix for the issue. No direct workaround is available at the application level. Applying the official patch is recommended.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/69xxx/CVE-2025-69252.json
- https://github.com/free5gc/free5gc/security/advisories/GHSA-v8cv-qvf6-9rpm
- https://nvd.nist.gov/vuln/detail/CVE-2025-69252
- https://github.com/free5gc/free5gc/issues/752
- https://github.com/free5gc/udm/commit/504b14458d156558b3c0ade7107b86b3d5e72998
- https://github.com/free5gc/udm/pull/76
