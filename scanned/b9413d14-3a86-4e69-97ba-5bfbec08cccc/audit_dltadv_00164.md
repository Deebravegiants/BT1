# [M] PYSEC-2023-80

## Summary
Severity: Medium
Advisory: PYSEC-2023-80
Aliases: CVE-2023-32675, GHSA-vxmm-cwh2-q762
Package: vyper
Published: 2023-05-19
Source: https://osv.dev/vulnerability/PYSEC-2023-80
Type: chain-advisory

## Affected
- PyPI: `vyper` — affected >=0 <02339dfda0f3caabad142060d511d10bfe93c520., >=0 <0.3.8

## Details
Vyper is a pythonic Smart Contract Language for the ethereum virtual machine. In contracts with more than one regular nonpayable function, it is possible to send funds to the default function, even if the default function is marked `nonpayable`. This applies to contracts compiled with vyper versions prior to 0.3.8. This issue was fixed by the removal of the global `calldatasize` check in commit `02339dfda`. Users are advised to upgrade to version 0.3.8. Users unable to upgrade should avoid use of nonpayable default functions.

## References
- https://github.com/vyperlang/vyper/security/advisories/GHSA-vxmm-cwh2-q762
- https://github.com/vyperlang/vyper/security/advisories/GHSA-vxmm-cwh2-q762
- https://github.com/vyperlang/vyper/security/advisories/GHSA-vxmm-cwh2-q762
- https://github.com/vyperlang/vyper/commit/02339dfda0f3caabad142060d511d10bfe93c520.
