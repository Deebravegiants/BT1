# [H] ALPINE-CVE-2022-30550

## Summary
Severity: High
Advisory: ALPINE-CVE-2022-30550
Ecosystem: Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-07-17
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-30550
Type: osv

## Affected
- Alpine:v3.17: `dovecot` — affected >=2.3 <2.3.19.1-r5
- Alpine:v3.18: `dovecot` — affected >=2.3 <2.3.19.1-r5
- Alpine:v3.19: `dovecot` — affected >=2.3 <2.3.19.1-r5
- Alpine:v3.20: `dovecot` — affected >=2.3 <2.3.19.1-r5
- Alpine:v3.21: `dovecot` — affected >=2.3 <2.3.19.1-r5
- Alpine:v3.22: `dovecot` — affected >=2.3 <2.3.19.1-r5
- Alpine:v3.23: `dovecot` — affected >=2.3 <2.3.19.1-r5
- Alpine:v3.24: `dovecot` — affected >=2.3 <2.3.19.1-r5

## Details
An issue was discovered in the auth component in Dovecot 2.2 and 2.3 before 2.3.20. When two passdb configuration entries exist with the same driver and args settings, incorrect username_filter and mechanism settings can be applied to passdb definitions. These incorrectly applied settings can lead to an unintended security configuration and can permit privilege escalation in certain configurations. The documentation does not advise against the use of passdb definitions that have the same driver and args settings. One such configuration would be where an administrator wishes to use the same PAM configuration or passwd file for both normal and master users but use the username_filter setting to restrict which of the users is able to be a master user.

## References
- https://security.alpinelinux.org/vuln/CVE-2022-30550
