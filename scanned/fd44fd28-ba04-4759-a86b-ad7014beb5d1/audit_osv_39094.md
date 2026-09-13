# [M] jq: Wild stack write via signed-integer overflow in decNumber D2U() macro

## Summary
Severity: Medium
Advisory: CVE-2026-43894
Aliases: GHSA-5v7p-2r57-2g4g
CVSS: 6.2 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-05-11
Source: https://osv.dev/vulnerability/CVE-2026-43894
Type: osv

## Details
jq is a command-line JSON processor. In 1.8.1 and earlier, when decNumberFromString is given a number literal of INT_MAX-1 (2147483646) digits, the D2U() macro overflows during signed-int arithmetic. The wrapped negative value bypasses the heap-allocation size check, causes the function to use a 30-byte stack buffer, and then writes ≈715 million 16-bit units (≈1.4 GiB) at an offset 1.43 GiB below the stack frame. The written content is fully attacker-controlled (the parsed decimal digits, packed 3-per-unit).

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/43xxx/CVE-2026-43894.json
- https://github.com/jqlang/jq/security/advisories/GHSA-5v7p-2r57-2g4g
- https://nvd.nist.gov/vuln/detail/CVE-2026-43894
