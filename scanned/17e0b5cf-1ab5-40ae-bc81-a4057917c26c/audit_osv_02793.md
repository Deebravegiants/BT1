# [H] ALPINE-CVE-2023-2603

## Summary
Severity: High
Advisory: ALPINE-CVE-2023-2603
Ecosystem: Alpine:v3.15, Alpine:v3.16, Alpine:v3.17
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-06-06
Source: https://osv.dev/vulnerability/ALPINE-CVE-2023-2603
Type: osv

## Affected
- Alpine:v3.15: `libcap` — affected >=0 <2.61-r1
- Alpine:v3.16: `libcap` — affected >=0 <2.64-r1
- Alpine:v3.17: `libcap` — affected >=0 <2.66-r1

## Details
A vulnerability was found in libcap. This issue occurs in the _libcap_strdup() function and can lead to an integer overflow if the input string is close to 4GiB.

## References
- https://security.alpinelinux.org/vuln/CVE-2023-2603
