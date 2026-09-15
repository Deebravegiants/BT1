# [H] Macvim's Insecure Usage of IPC Mechanisms

## Summary
Severity: High
Advisory: CVE-2023-41036
Aliases: GHSA-9jgj-jfwg-99fv
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-09-12
Source: https://osv.dev/vulnerability/CVE-2023-41036
Type: osv

## Details
Macvim is a text editor for MacOS. Prior to version 178, Macvim makes use of an insecure interprocess communication (IPC) mechanism which could lead to a privilege escalation. Distributed objects are a concept introduced by Apple which allow one program to vend an interface to another program. What is not made clear in the documentation is that this service can vend this interface to any other program on the machine. The impact of exploitation is a privilege escalation to root - this is likely to affect anyone who is not careful about the software they download and use MacVim to edit files that would require root privileges. Version 178 contains a fix for this issue.

## References
- https://github.com/macvim-dev/macvim/blob/d9de087dddadbfd82fcb5dc9734380a2f829bd0a/src/MacVim/MMAppController.h#L28
- https://github.com/macvim-dev/macvim/blob/d9de087dddadbfd82fcb5dc9734380a2f829bd0a/src/MacVim/MMBackend.h
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/41xxx/CVE-2023-41036.json
- https://github.com/macvim-dev/macvim/security/advisories/GHSA-9jgj-jfwg-99fv
- https://nvd.nist.gov/vuln/detail/CVE-2023-41036
- https://github.com/macvim-dev/macvim/commit/399b43e9e1dbf656a1780e87344f4d3c875e4cda
