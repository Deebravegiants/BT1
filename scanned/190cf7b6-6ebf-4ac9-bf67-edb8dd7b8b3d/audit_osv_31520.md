# [H] DreamFactory saveZipFile Command Injection Remote Code Execution Vulnerability

## Summary
Severity: High
Advisory: CVE-2025-13700
CVSS: 7.2 (CVSS:3.0/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-12-23
Source: https://osv.dev/vulnerability/CVE-2025-13700
Type: osv

## Details
DreamFactory saveZipFile Command Injection Remote Code Execution Vulnerability. This vulnerability allows remote attackers to execute arbitrary code on affected installations of DreamFactory. Authentication is required to exploit this vulnerability.

The specific flaw exists within the implementation of the saveZipFile method. The issue results from the lack of proper validation of a user-supplied string before using it to execute a system call. An attacker can leverage this vulnerability to execute code in the context of the service account. Was ZDI-CAN-26589.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/13xxx/CVE-2025-13700.json
- https://github.com/dreamfactorysoftware/df-core/commit/404a1783927f95999c71a0ff8f14130d385087fb
- https://nvd.nist.gov/vuln/detail/CVE-2025-13700
- https://www.zerodayinitiative.com/advisories/ZDI-25-1024/
