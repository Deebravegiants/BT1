# [H] ALPINE-CVE-2020-5291

## Summary
Severity: High
Advisory: ALPINE-CVE-2020-5291
Ecosystem: Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-03-31
Source: https://osv.dev/vulnerability/ALPINE-CVE-2020-5291
Type: osv

## Affected
- Alpine:v3.11: `bubblewrap` — affected >=0 <0.4.1-r0
- Alpine:v3.12: `bubblewrap` — affected >=0 <0.4.1-r0
- Alpine:v3.13: `bubblewrap` — affected >=0 <0.4.1-r0
- Alpine:v3.14: `bubblewrap` — affected >=0 <0.4.1-r0
- Alpine:v3.15: `bubblewrap` — affected >=0 <0.4.1-r0
- Alpine:v3.16: `bubblewrap` — affected >=0 <0.4.1-r0
- Alpine:v3.17: `bubblewrap` — affected >=0 <0.4.1-r0
- Alpine:v3.18: `bubblewrap` — affected >=0 <0.4.1-r0
- Alpine:v3.19: `bubblewrap` — affected >=0 <0.4.1-r0
- Alpine:v3.20: `bubblewrap` — affected >=0 <0.4.1-r0
- Alpine:v3.21: `bubblewrap` — affected >=0 <0.4.1-r0
- Alpine:v3.22: `bubblewrap` — affected >=0 <0.4.1-r0
- Alpine:v3.23: `bubblewrap` — affected >=0 <0.4.1-r0
- Alpine:v3.24: `bubblewrap` — affected >=0 <0.4.1-r0

## Details
Bubblewrap (bwrap) before version 0.4.1, if installed in setuid mode and the kernel supports unprivileged user namespaces, then the `bwrap --userns2` option can be used to make the setuid process keep running as root while being traceable. This can in turn be used to gain root permissions. Note that this only affects the combination of bubblewrap in setuid mode (which is typically used when unprivileged user namespaces are not supported) and the support of unprivileged user namespaces. Known to be affected are: * Debian testing/unstable, if unprivileged user namespaces enabled (not default) * Debian buster-backports, if unprivileged user namespaces enabled (not default) * Arch if using `linux-hardened`, if unprivileged user namespaces enabled (not default) * Centos 7 flatpak COPR, if unprivileged user namespaces enabled (not default) This has been fixed in the 0.4.1 release, and all affected users should update.

## References
- https://security.alpinelinux.org/vuln/CVE-2020-5291
