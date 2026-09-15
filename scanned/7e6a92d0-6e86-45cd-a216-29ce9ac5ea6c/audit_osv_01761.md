# [H] ALPINE-CVE-2020-14342

## Summary
Severity: High
Advisory: ALPINE-CVE-2020-14342
Ecosystem: Alpine:v3.11, Alpine:v3.13
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-09-09
Source: https://osv.dev/vulnerability/ALPINE-CVE-2020-14342
Type: osv

## Affected
- Alpine:v3.11: `cifs-utils` — affected >=5.6 <6.13-r0
- Alpine:v3.13: `cifs-utils` — affected >=5.6 <6.11-r0

## Details
It was found that cifs-utils' mount.cifs was invoking a shell when requesting the Samba password, which could be used to inject arbitrary commands. An attacker able to invoke mount.cifs with special permission, such as via sudo rules, could use this flaw to escalate their privileges.

## References
- https://security.alpinelinux.org/vuln/CVE-2020-14342
