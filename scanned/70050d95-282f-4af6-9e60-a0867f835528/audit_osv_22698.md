# [H] Axiomatic Bento4 avcinfo Ap4BitStream.cpp WriteBytes heap-based overflow

## Summary
Severity: High
Advisory: CVE-2022-3664
CVSS: 7.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L)
Published: 2022-10-26
Source: https://osv.dev/vulnerability/CVE-2022-3664
Type: osv

## Details
A vulnerability classified as critical has been found in Axiomatic Bento4. Affected is the function AP4_BitStream::WriteBytes of the file Ap4BitStream.cpp of the component avcinfo. The manipulation leads to heap-based buffer overflow. It is possible to launch the attack remotely. The exploit has been disclosed to the public and may be used. The identifier of this vulnerability is VDB-212004.

## References
- https://github.com/axiomatic-systems/Bento4/files/9746288/avcinfo_poc1.zip
- https://vuldb.com/?id.212004
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/3xxx/CVE-2022-3664.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-3664
- https://github.com/axiomatic-systems/Bento4/issues/794
