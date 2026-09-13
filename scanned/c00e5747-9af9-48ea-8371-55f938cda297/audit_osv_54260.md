# [M] Null pointer dereference in vorbis_deinit in stb_vorbis

## Summary
Severity: Medium
Advisory: CVE-2023-45680
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2023-10-20
Source: https://osv.dev/vulnerability/CVE-2023-45680
Type: osv

## Details
stb_vorbis is a single file MIT licensed library for processing ogg vorbis files. A crafted file may trigger memory allocation failure in `start_decoder`. In that case the function returns early, the `f->comment_list` is set to `NULL`, but `f->comment_list_length` is not reset. Later in `vorbis_deinit` it tries to dereference the `NULL` pointer. This issue may lead to denial of service.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/45xxx/CVE-2023-45680.json
- https://github.com/nothings/stb/blob/5736b15f7ea0ffb08dd38af21067c314d6a3aae9/stb_vorbis.c#L3660-L3666
- https://github.com/nothings/stb/blob/5736b15f7ea0ffb08dd38af21067c314d6a3aae9/stb_vorbis.c#L4208-L4215
- https://nvd.nist.gov/vuln/detail/CVE-2023-45680
- https://securitylab.github.com/advisories/GHSL-2023-145_GHSL-2023-151_stb_image_h/
