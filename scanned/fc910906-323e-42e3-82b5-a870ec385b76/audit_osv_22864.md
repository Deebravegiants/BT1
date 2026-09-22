# [M] ffmpeg QuickTime RPZA Video Encoder rpzaenc.c out-of-bounds

## Summary
Severity: Medium
Advisory: CVE-2022-3964
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:L)
Published: 2022-11-13
Source: https://osv.dev/vulnerability/CVE-2022-3964
Type: osv

## Details
A vulnerability classified as problematic has been found in ffmpeg. This affects an unknown part of the file libavcodec/rpzaenc.c of the component QuickTime RPZA Video Encoder. The manipulation of the argument y_size leads to out-of-bounds read. It is possible to initiate the attack remotely. The name of the patch is 92f9b28ed84a77138105475beba16c146bdaf984. It is recommended to apply a patch to fix this issue. The associated identifier of this vulnerability is VDB-213543.

## References
- https://git.ffmpeg.org/gitweb/ffmpeg.git/commit/92f9b28ed84a77138105475beba16c146bdaf984
- https://vuldb.com/?id.213543
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/3xxx/CVE-2022-3964.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-3964
- https://security.gentoo.org/glsa/202312-14
