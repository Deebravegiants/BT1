# [H] Attempt to free an uninitialized memory pointer in vorbis_deinit in stb_vorbis

## Summary
Severity: High
Advisory: CVE-2023-45679
CVSS: 7.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L)
Published: 2023-10-20
Source: https://osv.dev/vulnerability/CVE-2023-45679
Type: osv

## Details
stb_vorbis is a single file MIT licensed library for processing ogg vorbis files. A crafted file may trigger memory allocation failure in `start_decoder`. In that case the function returns early, but some of the pointers in `f->comment_list` are left initialized and later `setup_free` is called on these pointers in `vorbis_deinit`. This issue may lead to code execution.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/45xxx/CVE-2023-45679.json
- https://github.com/nothings/stb/blob/5736b15f7ea0ffb08dd38af21067c314d6a3aae9/stb_vorbis.c#L3660-L3677
- https://github.com/nothings/stb/blob/5736b15f7ea0ffb08dd38af21067c314d6a3aae9/stb_vorbis.c#L4208-L4215
- https://nvd.nist.gov/vuln/detail/CVE-2023-45679
- https://securitylab.github.com/advisories/GHSL-2023-145_GHSL-2023-151_stb_image_h/
