# [M] free5GC vulnerable to improper error handling in NEF with information exposure

## Summary
Severity: Medium
Advisory: CVE-2025-69253
Aliases: GHSA-cj2h-x8qm-xgwc
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N/E:U)
Published: 2026-02-24
Source: https://osv.dev/vulnerability/CVE-2025-69253
Type: osv

## Details
free5GC is an open-source project for 5th generation (5G) mobile core networks. Versions up to and including 1.4.1 of the User Data Repository are affected by Improper Error Handling with Information Exposure. The NEF component reliably leaks internal parsing error details (e.g., invalid character 'n' after top-level value) to remote clients, which can aid attackers in service fingerprinting. All deployments of free5GC using the Nnef_PfdManagement service may be vulnerable. free5gc/udr pull request 56 contains a patch. No direct workaround is available at the application level. Applying the official patch is recommended.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/69xxx/CVE-2025-69253.json
- https://github.com/free5gc/free5gc/security/advisories/GHSA-cj2h-x8qm-xgwc
- https://nvd.nist.gov/vuln/detail/CVE-2025-69253
- https://github.com/free5gc/free5gc/issues/753
- https://github.com/free5gc/udr/commit/754d23b03755ad59077ed529ce3b971e477080c4
- https://github.com/free5gc/udr/pull/56
