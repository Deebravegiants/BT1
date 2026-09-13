# [M] CVE-2025-33026

## Summary
Severity: Medium
Advisory: CVE-2025-33026
CVSS: 6.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N)
Published: 2025-04-15
Source: https://osv.dev/vulnerability/CVE-2025-33026
Type: osv

## Details
In PeaZip through 10.4.0, there is a Mark-of-the-Web Bypass Vulnerability. This vulnerability allows attackers to bypass the Mark-of-the-Web protection mechanism on affected installations of PeaZip. User interaction is required to exploit this vulnerability in that the target must visit a malicious page or open a malicious file. The specific flaw exists within the handling of archived files. When extracting files from a crafted archive that bears the Mark-of-the-Web, PeaZip does not propagate the Mark-of-the-Web to the extracted files. An attacker can leverage this vulnerability to execute arbitrary code in the context of the current user. NOTE: this is disputed because Mark-of-the-Web propagation can increase risk via security-warning habituation, and because the intended control sphere for file-origin metadata (e.g., HostUrl in Zone.Identifier) may be narrower than that for reading the file's content.

## References
- https://github.com/EnisAksu/Argonis/blob/main/CVEs/CVE-2025-33026%20%28PeaZip%29/CVE-2025-33026.md
- https://peazip.github.io/peazip-64bit.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/33xxx/CVE-2025-33026.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-33026
