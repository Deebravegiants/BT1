# [H] ALPINE-CVE-2021-27290

## Summary
Severity: High
Advisory: ALPINE-CVE-2021-27290
Ecosystem: Alpine:v3.13
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-03-12
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-27290
Type: osv

## Affected
- Alpine:v3.13: `nodejs` — affected >=0 <14.16.1-r1

## Details
ssri 5.2.2-8.0.0, fixed in 8.0.1, processes SRIs using a regular expression which is vulnerable to a denial of service. Malicious SRIs could take an extremely long time to process, leading to denial of service. This issue only affects consumers using the strict option.

## References
- https://security.alpinelinux.org/vuln/CVE-2021-27290
