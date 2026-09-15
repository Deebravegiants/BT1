# [C] CVE-2023-48031

## Summary
Severity: Critical
Advisory: CVE-2023-48031
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-11-17
Source: https://osv.dev/vulnerability/CVE-2023-48031
Type: osv

## Details
OpenSupports v4.11.0 is vulnerable to Unrestricted Upload of File with Dangerous Type. In the comment function, an attacker can bypass security restrictions and upload a .bat file by manipulating the file's magic bytes to masquerade as an allowed type. This can enable the attacker to execute arbitrary code or establish a reverse shell, leading to unauthorized file writes or control over the victim's station via a crafted file upload operation.

## References
- https://bugplorer.github.io/cve-opensupports/
- https://nitipoom-jar.github.io/CVE-2023-48031/
- https://nitipoom-jaroonchaipipat.github.io/security-research-portal/2023-48031
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/48xxx/CVE-2023-48031.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-48031
