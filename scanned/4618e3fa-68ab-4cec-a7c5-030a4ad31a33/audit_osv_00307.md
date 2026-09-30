# [H] ALPINE-CVE-2016-9587

## Summary
Severity: High
Advisory: ALPINE-CVE-2016-9587
Ecosystem: Alpine:v3.4, Alpine:v3.5
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-04-24
Source: https://osv.dev/vulnerability/ALPINE-CVE-2016-9587
Type: osv

## Affected
- Alpine:v3.4: `ansible` — affected >=0 <2.1.4.0-r0
- Alpine:v3.5: `ansible` — affected >=0 <2.2.1.0-r0

## Details
Ansible before versions 2.1.4, 2.2.1 is vulnerable to an improper input validation in Ansible's handling of data sent from client systems. An attacker with control over a client system being managed by Ansible and the ability to send facts back to the Ansible server could use this flaw to execute arbitrary code on the Ansible server using the Ansible server privileges.

## References
- https://security.alpinelinux.org/vuln/CVE-2016-9587
