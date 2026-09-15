# [H] ALPINE-CVE-2020-5260

## Summary
Severity: High
Advisory: ALPINE-CVE-2020-5260
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.8, Alpine:v3.9
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2020-04-14
Source: https://osv.dev/vulnerability/ALPINE-CVE-2020-5260
Type: osv

## Affected
- Alpine:v3.10: `git` — affected >=2.22.0 <2.22.3-r0
- Alpine:v3.11: `git` — affected >=2.22.0 <2.24.2-r0
- Alpine:v3.12: `git` — affected >=2.22.0 <2.26.1-r0
- Alpine:v3.13: `git` — affected >=2.22.0 <2.26.1-r0
- Alpine:v3.14: `git` — affected >=2.22.0 <2.26.1-r0
- Alpine:v3.15: `git` — affected >=2.22.0 <2.26.1-r0
- Alpine:v3.16: `git` — affected >=2.22.0 <2.26.1-r0
- Alpine:v3.17: `git` — affected >=2.22.0 <2.26.1-r0
- Alpine:v3.18: `git` — affected >=2.22.0 <2.26.1-r0
- Alpine:v3.19: `git` — affected >=2.22.0 <2.26.1-r0
- Alpine:v3.20: `git` — affected >=2.22.0 <2.26.1-r0
- Alpine:v3.21: `git` — affected >=2.22.0 <2.26.1-r0
- Alpine:v3.22: `git` — affected >=2.22.0 <2.26.1-r0
- Alpine:v3.23: `git` — affected >=2.22.0 <2.26.1-r0
- Alpine:v3.24: `git` — affected >=2.22.0 <2.26.1-r0
- Alpine:v3.8: `git` — affected >=2.22.0 <2.18.3-r0
- Alpine:v3.9: `git` — affected >=2.22.0 <2.20.3-r0

## Details
Affected versions of Git have a vulnerability whereby Git can be tricked into sending private credentials to a host controlled by an attacker. Git uses external "credential helper" programs to store and retrieve passwords or other credentials from secure storage provided by the operating system. Specially-crafted URLs that contain an encoded newline can inject unintended values into the credential helper protocol stream, causing the credential helper to retrieve the password for one server (e.g., good.example.com) for an HTTP request being made to another server (e.g., evil.example.com), resulting in credentials for the former being sent to the latter. There are no restrictions on the relationship between the two, meaning that an attacker can craft a URL that will present stored credentials for any host to a host of their choosing. The vulnerability can be triggered by feeding a malicious URL to git clone. However, the affected URLs look rather suspicious; the likely vector would be through systems which automatically clone URLs not visible to the user, such as Git submodules, or package systems built around Git. The problem has been patched in the versions published on April 14th, 2020, going back to v2.17.x. Anyone wishing to backport the change further can do so by applying commit 9a6bbee (the full release includes extra checks for git fsck, but that commit is sufficient to protect clients against the vulnerability). The patched versions are: 2.17.4, 2.18.3, 2.19.4, 2.20.3, 2.21.2, 2.22.3, 2.23.2, 2.24.2, 2.25.3, 2.26.1.

## References
- https://security.alpinelinux.org/vuln/CVE-2020-5260
