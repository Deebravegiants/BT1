# [M] ALPINE-CVE-2019-14864

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2019-14864
Ecosystem: Alpine:v3.10, Alpine:v3.9
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2020-01-02
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-14864
Type: osv

## Affected
- Alpine:v3.10: `ansible` — affected >=2.7.0 <2.8.8-r0
- Alpine:v3.9: `ansible` — affected >=2.7.0 <2.7.16-r0

## Details
Ansible, versions 2.9.x before 2.9.1, 2.8.x before 2.8.7 and Ansible versions 2.7.x before 2.7.15, is not respecting the flag no_log set it to True when Sumologic and Splunk callback plugins are used send tasks results events to collectors. This would discloses and collects any sensitive data.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-14864
