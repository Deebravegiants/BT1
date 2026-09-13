# [H] ClipShare Server Allows Local Privilege Escalation via DLL Hijacking

## Summary
Severity: High
Advisory: CVE-2025-49148
Aliases: GHSA-rc47-h83g-2r8j
CVSS: 7.3 (CVSS:3.1/AV:L/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H)
Published: 2025-06-11
Source: https://osv.dev/vulnerability/CVE-2025-49148
Type: osv

## Details
ClipShare is a lightweight and cross-platform tool for clipboard sharing. Prior to 3.8.5, ClipShare Server for Windows uses the default Windows DLL search order and loads system libraries like CRYPTBASE.dll and WindowsCodecs.dll from its own directory before the system path. A local, non-privileged user who can write to the folder containing clip_share.exe can place malicious DLLs there, leading to arbitrary code execution in the context of the server, and, if launched by an Administrator (or another elevated user), it results in a reliable local privilege escalation. This vulnerability is fixed in 3.8.5.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/49xxx/CVE-2025-49148.json
- https://github.com/thevindu-w/clip_share_server/security/advisories/GHSA-rc47-h83g-2r8j
- https://nvd.nist.gov/vuln/detail/CVE-2025-49148
