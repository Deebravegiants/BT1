# [H] ALPINE-CVE-2022-1271

## Summary
Severity: High
Advisory: ALPINE-CVE-2022-1271
Ecosystem: Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-08-31
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-1271
Type: osv

## Affected
- Alpine:v3.12: `gzip` — affected >=0 <1.12-r0
- Alpine:v3.13: `gzip` — affected >=0 <1.12-r0
- Alpine:v3.14: `gzip` — affected >=0 <1.12-r0
- Alpine:v3.15: `gzip` — affected >=0 <1.12-r0
- Alpine:v3.16: `gzip` — affected >=0 <1.12-r0
- Alpine:v3.17: `gzip` — affected >=0 <1.12-r0
- Alpine:v3.18: `gzip` — affected >=0 <1.12-r0
- Alpine:v3.19: `gzip` — affected >=0 <1.12-r0
- Alpine:v3.20: `gzip` — affected >=0 <1.12-r0
- Alpine:v3.21: `gzip` — affected >=0 <1.12-r0
- Alpine:v3.22: `gzip` — affected >=0 <1.12-r0
- Alpine:v3.23: `gzip` — affected >=0 <1.12-r0
- Alpine:v3.24: `gzip` — affected >=0 <1.12-r0
- Alpine:v3.12: `xz` — affected >=0 <5.2.5-r1
- Alpine:v3.13: `xz` — affected >=0 <5.2.5-r1
- Alpine:v3.14: `xz` — affected >=0 <5.2.5-r1
- Alpine:v3.15: `xz` — affected >=0 <5.2.5-r1
- Alpine:v3.16: `xz` — affected >=0 <5.2.5-r1
- Alpine:v3.17: `xz` — affected >=0 <5.2.5-r1
- Alpine:v3.18: `xz` — affected >=0 <5.2.5-r1
- Alpine:v3.19: `xz` — affected >=0 <5.2.5-r1
- Alpine:v3.20: `xz` — affected >=0 <5.2.5-r1
- Alpine:v3.21: `xz` — affected >=0 <5.2.5-r1
- Alpine:v3.22: `xz` — affected >=0 <5.2.5-r1
- Alpine:v3.23: `xz` — affected >=0 <5.2.5-r1

## Details
An arbitrary file write vulnerability was found in GNU gzip's zgrep utility. When zgrep is applied on the attacker's chosen file name (for example, a crafted file name), this can overwrite an attacker's content to an arbitrary attacker-selected file. This flaw occurs due to insufficient validation when processing filenames with two or more newlines where selected content and the target file names are embedded in crafted multi-line file names. This flaw allows a remote, low privileged attacker to force zgrep to write arbitrary files on the system.

## References
- https://security.alpinelinux.org/vuln/CVE-2022-1271
