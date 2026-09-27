# [M] free5GC has Improper Error Handling in UDM, Leading to Information Exposure

## Summary
Severity: Medium
Advisory: CVE-2025-69250
Aliases: GHSA-6w77-5pqh-83rm
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N/E:U)
Published: 2026-02-23
Source: https://osv.dev/vulnerability/CVE-2025-69250
Type: osv

## Details
free5gc UDM provides Unified Data Management (UDM) for free5GC, an open-source project for 5th generation (5G) mobile core networks. In versions up to and including 1.4.1, the service reliably leaks detailed internal error messages (e.g., strconv.ParseInt parsing errors) to remote clients when processing invalid pduSessionId inputs. This exposes implementation details and can be used for service fingerprinting. All deployments of free5GC using the UDM Nudm_UECM DELETE service may be vulnerable. free5gc/udm pull request 76 contains a fix for the issue. No direct workaround is available at the application level. Applying the official patch is recommended.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/69xxx/CVE-2025-69250.json
- https://github.com/free5gc/free5gc/security/advisories/GHSA-6w77-5pqh-83rm
- https://nvd.nist.gov/vuln/detail/CVE-2025-69250
- https://github.com/free5gc/free5gc/issues/750
- https://github.com/free5gc/udm/commit/504b14458d156558b3c0ade7107b86b3d5e72998
- https://github.com/free5gc/udm/pull/76
