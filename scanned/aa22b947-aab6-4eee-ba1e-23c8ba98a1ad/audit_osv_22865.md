# [M] ffmpeg QuickTime Graphics Video Encoder smcenc.c smc_encode_stream out-of-bounds

## Summary
Severity: Medium
Advisory: CVE-2022-3965
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:L)
Published: 2022-11-13
Source: https://osv.dev/vulnerability/CVE-2022-3965
Type: osv

## Details
A vulnerability classified as problematic was found in ffmpeg. This vulnerability affects the function smc_encode_stream of the file libavcodec/smcenc.c of the component QuickTime Graphics Video Encoder. The manipulation of the argument y_size leads to out-of-bounds read. The attack can be initiated remotely. The name of the patch is 13c13109759090b7f7182480d075e13b36ed8edd. It is recommended to apply a patch to fix this issue. The identifier of this vulnerability is VDB-213544.

## References
- https://git.ffmpeg.org/gitweb/ffmpeg.git/commit/13c13109759090b7f7182480d075e13b36ed8edd
- https://vuldb.com/?id.213544
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/3xxx/CVE-2022-3965.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-3965
- https://security.gentoo.org/glsa/202312-14
