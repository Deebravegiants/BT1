# [H] CVE-2024-33535

## Summary
Severity: High
Advisory: CVE-2024-33535
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2024-08-12
Source: https://osv.dev/vulnerability/CVE-2024-33535
Type: osv

## Details
An issue was discovered in Zimbra Collaboration (ZCS) 9.0 and 10.0. The vulnerability involves unauthenticated local file inclusion (LFI) in a web application, specifically impacting the handling of the packages parameter. Attackers can exploit this flaw to include arbitrary local files without authentication, potentially leading to unauthorized access to sensitive information. The vulnerability is limited to files within a specific directory.

## References
- https://wiki.zimbra.com/wiki/Zimbra_Releases/10.0.8#Security_Fixes
- https://wiki.zimbra.com/wiki/Zimbra_Releases/9.0.0/P40#Security_Fixes
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/33xxx/CVE-2024-33535.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-33535
