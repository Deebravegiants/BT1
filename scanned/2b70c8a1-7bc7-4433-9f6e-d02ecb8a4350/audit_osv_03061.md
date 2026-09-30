# [M] ALPINE-CVE-2024-35235

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2024-35235
Ecosystem: Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 6.7 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-06-11
Source: https://osv.dev/vulnerability/ALPINE-CVE-2024-35235
Type: osv

## Affected
- Alpine:v3.17: `cups` — affected >=0 <2.4.9-r0
- Alpine:v3.18: `cups` — affected >=0 <2.4.9-r0
- Alpine:v3.19: `cups` — affected >=0 <2.4.9-r0
- Alpine:v3.20: `cups` — affected >=0 <2.4.9-r0
- Alpine:v3.21: `cups` — affected >=0 <2.4.9-r0
- Alpine:v3.22: `cups` — affected >=0 <2.4.9-r0
- Alpine:v3.23: `cups` — affected >=0 <2.4.9-r0
- Alpine:v3.24: `cups` — affected >=0 <2.4.9-r0

## Details
OpenPrinting CUPS is an open source printing system for Linux and other Unix-like operating systems. In versions 2.4.8 and earlier, when starting the cupsd server with a Listen configuration item pointing to a symbolic link, the cupsd process can be caused to perform an arbitrary chmod of the provided argument, providing world-writable access to the target. Given that cupsd is often running as root, this can result in the change of permission of any user or system files to be world writable. Given the aforementioned Ubuntu AppArmor context, on such systems this vulnerability is limited to those files modifiable by the cupsd process. In that specific case it was found to be possible to turn the configuration of the Listen argument into full control over the cupsd.conf and cups-files.conf configuration files. By later setting the User and Group arguments in cups-files.conf, and printing with a printer configured by PPD with a `FoomaticRIPCommandLine` argument, arbitrary user and group (not root) command execution could be achieved, which can further be used on Ubuntu systems to achieve full root command execution. Commit ff1f8a623e090dee8a8aadf12a6a4b25efac143d contains a patch for the issue.

## References
- https://security.alpinelinux.org/vuln/CVE-2024-35235
