# [M] GPAC lsr_dec.c lsr_translate_coords integer overflow

## Summary
Severity: Medium
Advisory: CVE-2022-4202
CVSS: 6.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:L)
Published: 2022-11-29
Source: https://osv.dev/vulnerability/CVE-2022-4202
Type: osv

## Details
A vulnerability, which was classified as problematic, was found in GPAC 2.1-DEV-rev490-g68064e101-master. Affected is the function lsr_translate_coords of the file laser/lsr_dec.c. The manipulation leads to integer overflow. It is possible to launch the attack remotely. The exploit has been disclosed to the public and may be used. The name of the patch is b3d821c4ae9ba62b3a194d9dcb5e99f17bd56908. It is recommended to apply a patch to fix this issue. VDB-214518 is the identifier assigned to this vulnerability.

## References
- https://drive.google.com/file/d/1HVWa6IpAbvsMS5rx091RfjUB4GfXrMLE/view
- https://vuldb.com/?id.214518
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/4xxx/CVE-2022-4202.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-4202
- https://www.debian.org/security/2023/dsa-5411
- https://github.com/gpac/gpac/issues/2333
- https://github.com/gpac/gpac/commit/b3d821c4ae9ba62b3a194d9dcb5e99f17bd56908
