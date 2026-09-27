# [C] Bytecode Viewer v2.10.x Zip Slip

## Summary
Severity: Critical
Advisory: CVE-2022-21675
Aliases: GHSA-3wq9-j4fc-4wmc
CVSS: 9.9 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:H/A:H)
Published: 2022-01-12
Source: https://osv.dev/vulnerability/CVE-2022-21675
Type: osv

## Details
Bytecode Viewer (BCV) is a Java/Android reverse engineering suite. Versions of the package prior to 2.11.0 are vulnerable to Arbitrary File Write via Archive Extraction (AKA "Zip Slip"). The vulnerability is exploited using a specially crafted archive that holds directory traversal filenames (e.g. ../../evil.exe). The Zip Slip vulnerability can affect numerous archive formats, including zip, jar, tar, war, cpio, apk, rar and 7z. The attacker can then overwrite executable files and either invoke them remotely or wait for the system or user to call them, thus achieving remote command execution on the victim’s machine. The impact of a Zip Slip vulnerability would allow an attacker to create or overwrite existing files on the filesystem. In the context of a web application, a web shell could be placed within the application directory to achieve code execution. All users should upgrade to BCV v2.11.0 when possible to receive a patch. There are no recommended workarounds aside from upgrading.

## References
- https://github.com/Konloch/bytecode-viewer/releases/tag/v2.11.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/21xxx/CVE-2022-21675.json
- https://github.com/Konloch/bytecode-viewer/security/advisories/GHSA-3wq9-j4fc-4wmc
- https://nvd.nist.gov/vuln/detail/CVE-2022-21675
- https://github.com/Konloch/bytecode-viewer/commit/1ec02658fe6858162f5e6a24f97928de6696c5cb
- https://github.com/Konloch/bytecode-viewer/commit/c968e94b2c93da434a4ecfac6d08eda162d615d0
