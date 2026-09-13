# [H] ALPINE-CVE-2020-25646

## Summary
Severity: High
Advisory: ALPINE-CVE-2020-25646
Ecosystem: Alpine:v3.13, Alpine:v3.14
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2020-10-29
Source: https://osv.dev/vulnerability/ALPINE-CVE-2020-25646
Type: osv

## Affected
- Alpine:v3.13: `ansible` — affected >=0 <2.10.1-r0
- Alpine:v3.14: `ansible` — affected >=0 <2.10.1-r0

## Details
A flaw was found in Ansible Collection community.crypto. openssl_privatekey_info exposes private key in logs. This directly impacts confidentiality

## References
- https://security.alpinelinux.org/vuln/CVE-2020-25646
