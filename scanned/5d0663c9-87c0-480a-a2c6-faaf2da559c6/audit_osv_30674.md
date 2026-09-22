# [H] CVE-2024-54663

## Summary
Severity: High
Advisory: CVE-2024-54663
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2024-12-19
Source: https://osv.dev/vulnerability/CVE-2024-54663
Type: osv

## Details
An issue was discovered in the Webmail Classic UI in Zimbra Collaboration (ZCS) 9.0 and 10.0 and 10.1. A Local File Inclusion (LFI) vulnerability exists in the /h/rest endpoint, allowing authenticated remote attackers to include and access sensitive files in the WebRoot directory. Exploitation requires a valid auth token and involves crafting a malicious request targeting specific file paths.

## References
- https://wiki.zimbra.com/wiki/Zimbra_Releases/10.0.11#Security_Fixes
- https://wiki.zimbra.com/wiki/Zimbra_Releases/10.1.3#Security_Fixes
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/54xxx/CVE-2024-54663.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-54663
