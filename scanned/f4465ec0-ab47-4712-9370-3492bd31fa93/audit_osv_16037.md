# [H] CVE-2019-25078

## Summary
Severity: High
Advisory: CVE-2019-25078
Aliases: PYSEC-2022-43062
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-12-13
Source: https://osv.dev/vulnerability/CVE-2019-25078
Type: osv

## Details
A vulnerability classified as problematic was found in pacparser up to 1.3.x. Affected by this vulnerability is the function pacparser_find_proxy of the file src/pacparser.c. The manipulation of the argument url leads to buffer overflow. Attacking locally is a requirement. Upgrading to version 1.4.0 is able to address this issue. The name of the patch is 853e8f45607cb07b877ffd270c63dbcdd5201ad9. It is recommended to upgrade the affected component. The associated identifier of this vulnerability is VDB-215443.

## References
- https://github.com/manugarg/pacparser/releases/tag/v1.4.0
- https://github.com/manugarg/pacparser/issues/99
- https://vuldb.com/?id.215443
- https://github.com/manugarg/pacparser/commit/853e8f45607cb07b877ffd270c63dbcdd5201ad9
