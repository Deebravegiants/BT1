# [M] Wild address read in vorbis_decode_packet_rest in stb_vorbis

## Summary
Severity: Medium
Advisory: CVE-2023-45682
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2023-10-20
Source: https://osv.dev/vulnerability/CVE-2023-45682
Type: osv

## Details
stb_vorbis is a single file MIT licensed library for processing ogg vorbis files. A crafted file may trigger out of bounds read in `DECODE` macro when `var` is negative. As it can be seen in the definition of `DECODE_RAW` a negative `var` is a valid value. This issue may be used to leak internal memory allocation information.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/45xxx/CVE-2023-45682.json
- https://github.com/nothings/stb/blob/5736b15f7ea0ffb08dd38af21067c314d6a3aae9/stb_vorbis.c#L1717-L1729
- https://github.com/nothings/stb/blob/5736b15f7ea0ffb08dd38af21067c314d6a3aae9/stb_vorbis.c#L1754-L1756
- https://github.com/nothings/stb/blob/5736b15f7ea0ffb08dd38af21067c314d6a3aae9/stb_vorbis.c#L3231
- https://nvd.nist.gov/vuln/detail/CVE-2023-45682
- https://securitylab.github.com/advisories/GHSL-2023-145_GHSL-2023-151_stb_image_h/
