# [C] cpdb-libs vulnerable to buffer overflows via scanf

## Summary
Severity: Critical
Advisory: CVE-2023-34095
Aliases: GHSA-25j7-9gfc-f46x
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-06-14
Source: https://osv.dev/vulnerability/CVE-2023-34095
Type: osv

## Details
cpdb-libs provides frontend and backend libraries for the Common Printing Dialog Backends (CPDB) project. In versions 1.0 through 2.0b4, cpdb-libs is vulnerable to buffer overflows via improper use of `scanf(3)`. cpdb-libs uses the `fscanf()` and `scanf()` functions to parse command lines and configuration files, dropping the read string components into fixed-length buffers, but does not limit the length of the strings to be read by `fscanf()` and `scanf()` causing buffer overflows when a string is longer than 1023 characters. A patch for this issue is available at commit f181bd1f14757c2ae0f17cc76dc20421a40f30b7. As all buffers have a length of 1024 characters, the patch limits the maximum string length to be read to 1023 by replacing all occurrences of `%s` with `%1023s` in all calls of the `fscanf()` and `scanf()` functions.

## References
- http://www.openwall.com/lists/oss-security/2023/06/14/7
- https://github.com/OpenPrinting/cpdb-libs/blob/85555fba64d34f53a2fce099b0488904cc48ed35/cpdb/cpdb-frontend.c#L372
- https://github.com/OpenPrinting/cpdb-libs/blob/85555fba64d34f53a2fce099b0488904cc48ed35/tools/cpdb-text-frontend.c#L362
- https://github.com/OpenPrinting/cpdb-libs/blob/85555fba64d34f53a2fce099b0488904cc48ed35/tools/cpdb-text-frontend.c#L453
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/34xxx/CVE-2023-34095.json
- https://github.com/OpenPrinting/cpdb-libs/security/advisories/GHSA-25j7-9gfc-f46x
- https://nvd.nist.gov/vuln/detail/CVE-2023-34095
- https://github.com/OpenPrinting/cpdb-libs/commit/f181bd1f14757c2ae0f17cc76dc20421a40f30b7
