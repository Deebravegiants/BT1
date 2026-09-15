# [M] ALPINE-CVE-2026-43894

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2026-43894
Ecosystem: Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-05-11
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-43894
Type: osv

## Affected
- Alpine:v3.22: `jq` — affected >=0 <1.8.2-r0
- Alpine:v3.23: `jq` — affected >=0 <1.8.2-r0
- Alpine:v3.24: `jq` — affected >=0 <1.8.2-r0

## Details
jq is a command-line JSON processor. In 1.8.1 and earlier, when decNumberFromString is given a number literal of INT_MAX-1 (2147483646) digits, the D2U() macro overflows during signed-int arithmetic. The wrapped negative value bypasses the heap-allocation size check, causes the function to use a 30-byte stack buffer, and then writes ≈715 million 16-bit units (≈1.4 GiB) at an offset 1.43 GiB below the stack frame. The written content is fully attacker-controlled (the parsed decimal digits, packed 3-per-unit).

## References
- https://security.alpinelinux.org/vuln/CVE-2026-43894
