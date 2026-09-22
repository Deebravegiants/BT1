# [M] CVE-2023-0687

## Summary
Severity: Medium
Advisory: CVE-2023-0687
CVSS: 4.6 (CVSS:3.1/AV:A/AC:H/PR:L/UI:N/S:U/C:L/I:L/A:L)
Published: 2023-02-06
Source: https://osv.dev/vulnerability/CVE-2023-0687
Type: osv

## Details
A vulnerability was found in GNU C Library 2.38. It has been declared as critical. This vulnerability affects the function __monstartup of the file gmon.c of the component Call Graph Monitor. The manipulation leads to buffer overflow. It is recommended to apply a patch to fix this issue. VDB-220246 is the identifier assigned to this vulnerability. NOTE: The real existence of this vulnerability is still doubted at the moment. The inputs that induce this vulnerability are basically addresses of the running application that is built with gmon enabled. It's basically trusted input or input that needs an actual security flaw to be compromised or controlled.

## References
- https://patchwork.sourceware.org/project/glibc/patch/20230204114138.5436-1-leo%40yuriev.ru/
- https://vuldb.com/?ctiid.220246
- https://vuldb.com/?id.220246
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/0xxx/CVE-2023-0687.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-0687
- https://sourceware.org/bugzilla/show_bug.cgi?id=29444
