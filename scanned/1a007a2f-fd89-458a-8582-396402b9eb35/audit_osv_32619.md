# [M] CVE-2025-33028

## Summary
Severity: Medium
Advisory: CVE-2025-33028
CVSS: 6.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N)
Published: 2025-04-15
Source: https://osv.dev/vulnerability/CVE-2025-33028
Type: osv

## Details
In WinZip through 29.0, there is a Mark-of-the-Web Bypass Vulnerability because of an incomplete fix for CVE-2024-8811. This vulnerability allows attackers to bypass the Mark-of-the-Web protection mechanism on affected installations of WinZip. User interaction is required to exploit this vulnerability in that the target must visit a malicious page or open a malicious file. The specific flaw exists within the handling of archived files. When extracting files from a crafted archive that bears the Mark-of-the-Web, WinZip does not propagate the Mark-of-the-Web to the extracted files. An attacker can leverage this vulnerability to execute arbitrary code in the context of the current user. NOTE: a third party has reported that this is a false positive, and has observed that the original CVE-2025-33028.md file has been deleted on GitHub. Also, this is disputed because Mark-of-the-Web propagation can increase risk via security-warning habituation, and because the intended control sphere for file-origin metadata (e.g., HostUrl in Zone.Identifier) may be narrower than that for reading the file's content.

## References
- https://github.com/EnisAksu/Argonis/blob/main/CVEs/CVE-2025-33028%20%28WinZip%29/CVE-2025-33028.md
- https://kb.winzip.com/help/help_whatsnew.htm
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/33xxx/CVE-2025-33028.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-33028
- https://github.com/EnisAksu/Argonis/commit/5e1ff4e5f4fdb3f32aab465f7b429e0b91299d1d
