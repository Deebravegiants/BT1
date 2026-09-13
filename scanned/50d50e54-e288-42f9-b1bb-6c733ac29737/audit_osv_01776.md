# [M] ALPINE-CVE-2020-14367

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2020-14367
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.9
CVSS: 6.0 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:N/I:H/A:H)
Published: 2020-08-24
Source: https://osv.dev/vulnerability/ALPINE-CVE-2020-14367
Type: osv

## Affected
- Alpine:v3.10: `chrony` — affected >=0 <3.5.1-r0
- Alpine:v3.11: `chrony` — affected >=0 <3.5.1-r0
- Alpine:v3.12: `chrony` — affected >=0 <3.5.1-r0
- Alpine:v3.13: `chrony` — affected >=0 <3.5.1-r0
- Alpine:v3.14: `chrony` — affected >=0 <3.5.1-r0
- Alpine:v3.15: `chrony` — affected >=0 <3.5.1-r0
- Alpine:v3.16: `chrony` — affected >=0 <3.5.1-r0
- Alpine:v3.17: `chrony` — affected >=0 <3.5.1-r0
- Alpine:v3.18: `chrony` — affected >=0 <3.5.1-r0
- Alpine:v3.19: `chrony` — affected >=0 <3.5.1-r0
- Alpine:v3.20: `chrony` — affected >=0 <3.5.1-r0
- Alpine:v3.21: `chrony` — affected >=0 <3.5.1-r0
- Alpine:v3.22: `chrony` — affected >=0 <3.5.1-r0
- Alpine:v3.23: `chrony` — affected >=0 <3.5.1-r0
- Alpine:v3.24: `chrony` — affected >=0 <3.5.1-r0
- Alpine:v3.9: `chrony` — affected >=0 <3.4-r2

## Details
A flaw was found in chrony versions before 3.5.1 when creating the PID file under the /var/run/chrony folder. The file is created during chronyd startup while still running as the root user, and when it's opened for writing, chronyd does not check for an existing symbolic link with the same file name. This flaw allows an attacker with privileged access to create a symlink with the default PID file name pointing to any destination file in the system, resulting in data loss and a denial of service due to the path traversal.

## References
- https://security.alpinelinux.org/vuln/CVE-2020-14367
