# [M] BIT-python-2023-38898

## Summary
Severity: Medium
Advisory: BIT-python-2023-38898
Aliases: CVE-2023-38898, PSF-2023-7
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-python-2023-38898
Type: osv

## Affected
- Bitnami: `python` — affected >=3.13.0-alpha0

## Details
An issue in Python cpython v.3.7 allows an attacker to obtain sensitive information via the _asyncio._swap_current_task component. NOTE: this is disputed by the vendor because (1) neither 3.7 nor any other release is affected (it is a bug in some 3.12 pre-releases); (2) there are no common scenarios in which an adversary can call _asyncio._swap_current_task but does not already have the ability to call arbitrary functions; and (3) there are no common scenarios in which sensitive information, which is not already accessible to an adversary, becomes accessible through this bug.

## References
- https://github.com/python/cpython/issues/105987
