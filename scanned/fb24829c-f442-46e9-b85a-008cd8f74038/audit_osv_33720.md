# [H] Notepad++ Privilege Escalation in Installer via Uncontrolled Executable Search Path

## Summary
Severity: High
Advisory: CVE-2025-49144
Aliases: GHSA-9vx8-v79m-6m24
CVSS: 7.3 (CVSS:3.1/AV:L/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H)
Published: 2025-06-23
Source: https://osv.dev/vulnerability/CVE-2025-49144
Type: osv

## Details
Notepad++ is a free and open-source source code editor. In versions 8.8.1 and prior, a privilege escalation vulnerability exists in the Notepad++ v8.8.1 installer that allows unprivileged users to gain SYSTEM-level privileges through insecure executable search paths. An attacker could use social engineering or clickjacking to trick users into downloading both the legitimate installer and a malicious executable to the same directory (typically Downloads folder - which is known as Vulnerable directory). Upon running the installer, the attack executes automatically with SYSTEM privileges. This issue has been fixed and will be released in version 8.8.2.

## References
- https://drive.google.com/drive/folders/11yeUSWgqHvt4Bz5jO3ilRRfcpQZ6Gvpn
- https://www.vicarius.io/vsociety/posts/cve-2025-49144-detect-notepad-vulnerability
- https://www.vicarius.io/vsociety/posts/cve-2025-49144-detect-notepad-vulnerability-1
- https://www.vicarius.io/vsociety/posts/cve-2025-49144-mitigate-notepad-vulnerability
- https://www.vicarius.io/vsociety/posts/cve-2025-49144-mitigate-notepad-vulnerability-1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/49xxx/CVE-2025-49144.json
- https://github.com/notepad-plus-plus/notepad-plus-plus/security/advisories/GHSA-9vx8-v79m-6m24
- https://nvd.nist.gov/vuln/detail/CVE-2025-49144
- https://github.com/notepad-plus-plus/notepad-plus-plus/commit/f2346ea00d5b4d907ed39d8726b38d77c8198f30
