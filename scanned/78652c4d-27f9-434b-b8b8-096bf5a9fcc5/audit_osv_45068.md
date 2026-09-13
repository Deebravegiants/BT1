# [H] PYSEC-2024-87

## Summary
Severity: High
Advisory: PYSEC-2024-87
Aliases: CVE-2024-8948, GHSA-vh3x-525m-jp4r, PYSEC-2024-88, PYSEC-2024-89
Ecosystem: PyPI
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-09-17
Source: https://osv.dev/vulnerability/PYSEC-2024-87
Type: osv

## Affected
- PyPI: `micropython-copy` — affected >=0 <908ab1ceca15ee6fd0ef82ca4cba770a3ec41894

## Details
A vulnerability was found in MicroPython 1.23.0. It has been rated as critical. Affected by this issue is the function mpz_as_bytes of the file py/objint.c. The manipulation leads to heap-based buffer overflow. The attack may be launched remotely. The exploit has been disclosed to the public and may be used. The patch is identified as 908ab1ceca15ee6fd0ef82ca4cba770a3ec41894. It is recommended to apply a patch to fix this issue. In micropython objint component, converting zero from int to bytes leads to heap buffer-overflow-write at mpz_as_bytes.

## References
- https://vuldb.com/?id.277766
- https://vuldb.com/?ctiid.277766
- https://vuldb.com/?submit.409317
- https://github.com/micropython/micropython/issues/13041
- https://github.com/micropython/micropython/commit/908ab1ceca15ee6fd0ef82ca4cba770a3ec41894
