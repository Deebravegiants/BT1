# [H] ALPINE-CVE-2026-4878

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-4878
Ecosystem: Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-04-09
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-4878
Type: osv

## Affected
- Alpine:v3.20: `libcap` — affected >=0 <2.78-r0
- Alpine:v3.21: `libcap` — affected >=0 <2.78-r0
- Alpine:v3.22: `libcap` — affected >=0 <2.78-r0
- Alpine:v3.23: `libcap` — affected >=0 <2.78-r0
- Alpine:v3.24: `libcap` — affected >=0 <2.78-r0

## Details
A flaw was found in libcap. A local unprivileged user can exploit a Time-of-check-to-time-of-use (TOCTOU) race condition in the `cap_set_file()` function. This allows an attacker with write access to a parent directory to redirect file capability updates to an attacker-controlled file. By doing so, capabilities can be injected into or stripped from unintended executables, leading to privilege escalation.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-4878
