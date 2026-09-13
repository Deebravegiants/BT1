# [C] Dataease H2 Database Remote Code Execution (RCE) Bypass Vulnerability

## Summary
Severity: Critical
Advisory: CVE-2025-49002
CVSS: 9.0 (CVSS:4.0/AV:N/AC:H/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:P)
Published: 2025-06-03
Source: https://osv.dev/vulnerability/CVE-2025-49002
Type: osv

## Details
DataEase is an open source business intelligence and data visualization tool. Versions prior to version 2.10.10 have a flaw in the patch for CVE-2025-32966 that allow the patch to be bypassed through case insensitivity because INIT and RUNSCRIPT are prohibited. The vulnerability has been fixed in v2.10.10. No known workarounds are available.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/49xxx/CVE-2025-49002.json
- https://github.com/dataease/dataease/security/advisories/GHSA-999m-jv2p-5h34
- https://github.com/dataease/dataease/security/advisories/GHSA-h7hj-4j78-cvc7
- https://nvd.nist.gov/vuln/detail/CVE-2025-49002
