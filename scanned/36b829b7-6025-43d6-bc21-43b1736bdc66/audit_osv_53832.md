# [H] CVE-2023-2789

## Summary
Severity: High
Advisory: CVE-2023-2789
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-05-18
Source: https://osv.dev/vulnerability/CVE-2023-2789
Type: osv

## Details
A vulnerability was found in GNU cflow 1.7. It has been rated as problematic. This issue affects the function func_body/parse_variable_declaration of the file parser.c. The manipulation leads to denial of service. The exploit has been disclosed to the public and may be used. The identifier VDB-229373 was assigned to this vulnerability. NOTE: The vendor was contacted early about this disclosure but did not respond in any way.

## References
- https://vuldb.com/?ctiid.229373
- https://vuldb.com/?id.229373
- https://github.com/DaisyPo/fuzzing-vulncollect/blob/main/cflow/stack-overflow/parser.c/README.md
- https://github.com/DaisyPo/fuzzing-vulncollect/files/11343936/poc-file.zip
