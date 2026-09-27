# [H] ALPINE-CVE-2017-16651

## Summary
Severity: High
Advisory: ALPINE-CVE-2017-16651
Ecosystem: Alpine:v3.3, Alpine:v3.4, Alpine:v3.5
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-11-09
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-16651
Type: osv

## Affected
- Alpine:v3.3: `roundcubemail` — affected >=0 <1.1.10-r0
- Alpine:v3.4: `roundcubemail` — affected >=0 <1.2.7-r0
- Alpine:v3.5: `roundcubemail` — affected >=0 <1.2.7-r0

## Details
Roundcube Webmail before 1.1.10, 1.2.x before 1.2.7, and 1.3.x before 1.3.3 allows unauthorized access to arbitrary files on the host's filesystem, including configuration files, as exploited in the wild in November 2017. The attacker must be able to authenticate at the target system with a valid username/password as the attack requires an active session. The issue is related to file-based attachment plugins and _task=settings&_action=upload-display&_from=timezone requests.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-16651
