# [M] CVE-2021-44568

## Summary
Severity: Medium
Advisory: CVE-2021-44568
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2022-02-21
Source: https://osv.dev/vulnerability/CVE-2021-44568
Type: osv

## Details
Two heap-overflow vulnerabilities exist in openSUSE/libsolv libsolv through 13 Dec 2020 in the decisionmap variable via the resolve_dependencies function at src/solver.c (line 1940 & line 1995), which could cause a remote Denial of Service.

## References
- https://github.com/openSUSE/libsolv/issues/425
- https://github.com/yangjiageng/PoC/blob/master/libsolv-PoCs/resolve_dependencies-1940
- https://github.com/yangjiageng/PoC/blob/master/libsolv-PoCs/resolve_dependencies-1995
