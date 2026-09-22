# [C] PYSEC-2023-256

## Summary
Severity: Critical
Advisory: PYSEC-2023-256
Aliases: CVE-2023-7152, PYSEC-2023-257, PYSEC-2023-258, PYSEC-2023-259
Ecosystem: PyPI
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-12-29
Source: https://osv.dev/vulnerability/PYSEC-2023-256
Type: osv

## Affected
- PyPI: `micropython-copy` — affected >=0 <8b24aa36ba978eafc6114b6798b47b7bfecdca26

## Details
A vulnerability, which was classified as critical, has been found in MicroPython 1.21.0/1.22.0-preview. Affected by this issue is the function poll_set_add_fd of the file extmod/modselect.c. The manipulation leads to use after free. The exploit has been disclosed to the public and may be used. The patch is identified as 8b24aa36ba978eafc6114b6798b47b7bfecdca26. It is recommended to apply a patch to fix this issue. VDB-249158 is the identifier assigned to this vulnerability.

## References
- https://vuldb.com/?id.249158
- https://vuldb.com/?ctiid.249158
- https://github.com/micropython/micropython/issues/12887
- https://github.com/jimmo/micropython/commit/8b24aa36ba978eafc6114b6798b47b7bfecdca26
