# [H] Rizin vulnerable to Integer Overflow in C++ demangler logic

## Summary
Severity: High
Advisory: CVE-2023-40022
Aliases: GHSA-92h6-wwc2-53cq
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2023-08-24
Source: https://osv.dev/vulnerability/CVE-2023-40022
Type: osv

## Details
Rizin is a UNIX-like reverse engineering framework and command-line toolset. Versions 0.6.0 and prior are vulnerable to integer overflow in `consume_count` of `src/gnu_v2/cplus-dem.c`. The overflow check is valid logic but, is missing the modulus if the block once compiled. The compiler sees this block as unreachable code since the prior statement is multiplication by 10 and fails to consider overflow assuming the count will always be a multiple of 10. Rizin version 0.6.1 contains a fix for the issue. A temporary workaround would be disabling C++ demangling using the configuration option `bin.demangle=false`.

## References
- https://github.com/rizinorg/rz-libdemangle/blob/main/src/gnu_v2/cplus-dem.c#L419
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/40xxx/CVE-2023-40022.json
- https://github.com/rizinorg/rizin/security/advisories/GHSA-92h6-wwc2-53cq
- https://nvd.nist.gov/vuln/detail/CVE-2023-40022
- https://github.com/rizinorg/rizin/pull/3753
- https://github.com/rizinorg/rz-libdemangle/commit/51d016750e704b27ab8ace23c0f72acabca67018
- https://github.com/rizinorg/rz-libdemangle/pull/54
