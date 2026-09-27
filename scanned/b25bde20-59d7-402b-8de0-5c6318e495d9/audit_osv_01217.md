# [H] ALPINE-CVE-2018-6196

## Summary
Severity: High
Advisory: ALPINE-CVE-2018-6196
Ecosystem: Alpine:v3.23
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-01-25
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-6196
Type: osv

## Affected
- Alpine:v3.23: `w3m` — affected >=0 <0.5.3_git20241203-r0

## Details
w3m through 0.5.3 is prone to an infinite recursion flaw in HTMLlineproc0 because the feed_table_block_tag function in table.c does not prevent a negative indent value.

## References
- https://security.alpinelinux.org/vuln/CVE-2018-6196
