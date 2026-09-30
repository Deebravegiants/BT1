# [M] Off-by-one heap buffer write in start_decoder in stb_vorbis

## Summary
Severity: Medium
Advisory: CVE-2023-45678
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:L)
Published: 2023-10-20
Source: https://osv.dev/vulnerability/CVE-2023-45678
Type: osv

## Details
stb_vorbis is a single file MIT licensed library for processing ogg vorbis files. A crafted file may trigger out of buffer write in `start_decoder` because at maximum `m->submaps` can be 16 but `submap_floor` and `submap_residue` are declared as arrays of 15 elements. This issue may lead to code execution.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/45xxx/CVE-2023-45678.json
- https://github.com/nothings/stb/blob/5736b15f7ea0ffb08dd38af21067c314d6a3aae9/stb_vorbis.c#L4074-L4079
- https://github.com/nothings/stb/blob/5736b15f7ea0ffb08dd38af21067c314d6a3aae9/stb_vorbis.c#L753-L760
- https://nvd.nist.gov/vuln/detail/CVE-2023-45678
- https://securitylab.github.com/advisories/GHSL-2023-145_GHSL-2023-151_stb_image_h/
