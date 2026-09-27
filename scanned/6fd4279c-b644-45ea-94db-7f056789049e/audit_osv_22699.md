# [H] Axiomatic Bento4 mp42ts Ap4LinearReader.cpp Advance use after free

## Summary
Severity: High
Advisory: CVE-2022-3666
CVSS: 7.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L)
Published: 2022-10-26
Source: https://osv.dev/vulnerability/CVE-2022-3666
Type: osv

## Details
A vulnerability, which was classified as critical, has been found in Axiomatic Bento4. Affected by this issue is the function AP4_LinearReader::Advance of the file Ap4LinearReader.cpp of the component mp42ts. The manipulation leads to use after free. The attack may be launched remotely. The exploit has been disclosed to the public and may be used. VDB-212006 is the identifier assigned to this vulnerability.

## References
- https://github.com/axiomatic-systems/Bento4/files/9744391/mp42ts_poc.zip
- https://vuldb.com/?id.212006
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/3xxx/CVE-2022-3666.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-3666
- https://github.com/axiomatic-systems/Bento4/issues/793
