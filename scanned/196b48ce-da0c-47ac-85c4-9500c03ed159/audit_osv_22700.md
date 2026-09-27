# [H] Axiomatic Bento4 mp42aac Ap4ByteStream.cpp WritePartial heap-based overflow

## Summary
Severity: High
Advisory: CVE-2022-3667
CVSS: 7.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L)
Published: 2022-10-26
Source: https://osv.dev/vulnerability/CVE-2022-3667
Type: osv

## Details
A vulnerability, which was classified as critical, was found in Axiomatic Bento4. This affects the function AP4_MemoryByteStream::WritePartial of the file Ap4ByteStream.cpp of the component mp42aac. The manipulation leads to heap-based buffer overflow. It is possible to initiate the attack remotely. The exploit has been disclosed to the public and may be used. The associated identifier of this vulnerability is VDB-212007.

## References
- https://github.com/17ssDP/fuzzer_crashes/blob/main/Bento4/mp42aac-hbo-01
- https://vuldb.com/?id.212007
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/3xxx/CVE-2022-3667.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-3667
- https://github.com/axiomatic-systems/Bento4/issues/789
