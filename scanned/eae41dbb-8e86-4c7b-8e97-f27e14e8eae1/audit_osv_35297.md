# [C] CVE-2025-70831

## Summary
Severity: Critical
Advisory: CVE-2025-70831
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-02-20
Source: https://osv.dev/vulnerability/CVE-2025-70831
Type: osv

## Details
A Remote Code Execution (RCE) vulnerability was found in Smanga 3.2.7 in the /php/path/rescan.php interface. The application fails to properly sanitize user-supplied input in the mediaId parameter before using it in a system shell command. This allows an unauthenticated attacker to inject arbitrary operating system commands, leading to complete server compromise.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/70xxx/CVE-2025-70831.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-70831
- https://github.com/LX-66-LX/cve/issues/5
