# [M] Axiomatic Bento4 mp4hls Ap4Mp4AudioInfo.cpp ReadBits heap-based overflow

## Summary
Severity: Medium
Advisory: CVE-2022-3784
CVSS: 6.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:L)
Published: 2022-10-31
Source: https://osv.dev/vulnerability/CVE-2022-3784
Type: osv

## Details
A vulnerability classified as critical was found in Axiomatic Bento4 5e7bb34. Affected by this vulnerability is the function AP4_Mp4AudioDsiParser::ReadBits of the file Ap4Mp4AudioInfo.cpp of the component mp4hls. The manipulation leads to heap-based buffer overflow. The attack can be launched remotely. The exploit has been disclosed to the public and may be used. The associated identifier of this vulnerability is VDB-212563.

## References
- https://github.com/axiomatic-systems/Bento4/files/9849116/mp42hls_ReadBits_Ap4Mp4AudioInfo66.zip
- https://vuldb.com/?id.212563
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/3xxx/CVE-2022-3784.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-3784
- https://github.com/axiomatic-systems/Bento4/issues/806
