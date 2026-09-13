# [H] ALPINE-CVE-2019-3500

## Summary
Severity: High
Advisory: ALPINE-CVE-2019-3500
Ecosystem: Alpine:v3.7
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-01-02
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-3500
Type: osv

## Affected
- Alpine:v3.7: `aria2` — affected >=0 <1.33.1-r1

## Details
aria2c in aria2 1.33.1, when --log is used, can store an HTTP Basic Authentication username and password in a file, which might allow local users to obtain sensitive information by reading this file.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-3500
