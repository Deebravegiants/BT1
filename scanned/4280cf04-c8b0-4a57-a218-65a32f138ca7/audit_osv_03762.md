# [H] ALPINE-CVE-2026-48092

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-48092
Ecosystem: Alpine:v3.24
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:H)
Published: 2026-06-05
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-48092
Type: osv

## Affected
- Alpine:v3.24: `7zip` — affected >=0 <26.01-r0

## Details
7-Zip is a file archiver with a high compression ratio. Versions 9.34 through 26.00 contain a heap memory disclosure via SquashFS fragment offset integer overflow on 32-bit builds. 32-bit integer overflow in the SquashFS ReadBlock function allows an attacker-controlled node.Offset value to bypass the fragment bounds check, causing memcpy to read heap memory preceding the cache buffer into the extracted file. The vulnerability is exploitable only on 32-bit builds of 7-Zip where size_t is 32 bits, allowing the addition offsetInBlock + blockSize to wrap modulo 2³². On 64-bit builds the addition is promoted to 64 bits and the check correctly rejects the input. Version 26.01 patches the issue.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-48092
