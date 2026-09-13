# [M] free5GC has Improper Input Validation in UDM UEAU Service

## Summary
Severity: Medium
Advisory: CVE-2026-27642
Aliases: GHSA-h4wg-rp7m-8xx4
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N/E:U)
Published: 2026-02-24
Source: https://osv.dev/vulnerability/CVE-2026-27642
Type: osv

## Details
free5gc UDM provides Unified Data Management (UDM) for free5GC, an open-source project for 5th generation (5G) mobile core networks. In versions up to and including 1.4.1, remote attackers can inject control characters (e.g., %00) into the supi parameter, triggering internal URL parsing errors (net/url: invalid control character). This exposes system-level error details and can be used for service fingerprinting. All deployments of free5GC using the UDM Nudm_UEAU service may be affected. free5gc/udm pull request 75 contains a fix for the issue. No direct workaround is available at the application level. Applying the official patch is recommended.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/27xxx/CVE-2026-27642.json
- https://github.com/free5gc/free5gc/security/advisories/GHSA-h4wg-rp7m-8xx4
- https://nvd.nist.gov/vuln/detail/CVE-2026-27642
- https://github.com/free5gc/free5gc/issues/749
- https://github.com/free5gc/udm/commit/a7af2321ddea6368c43835f90f6d1b9d67dd2ea1
- https://github.com/free5gc/udm/pull/75
