# [H] Heap buffer out of bounds write in start_decoder in stb_vorbis

## Summary
Severity: High
Advisory: CVE-2023-45677
CVSS: 7.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L)
Published: 2023-10-20
Source: https://osv.dev/vulnerability/CVE-2023-45677
Type: osv

## Details
stb_vorbis is a single file MIT licensed library for processing ogg vorbis files. A crafted file may trigger out of bounds write in `f->vendor[len] = (char)'\0';`. The root cause is that if `len` read in `start_decoder` is a negative number and `setup_malloc` successfully allocates memory in that case, but memory write is done with a negative index `len`. Similarly if len is INT_MAX the integer overflow len+1 happens in `f->vendor = (char*)setup_malloc(f, sizeof(char) * (len+1));` and `f->comment_list[i] = (char*)setup_malloc(f, sizeof(char) * (len+1));`. This issue may lead to code execution.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/45xxx/CVE-2023-45677.json
- https://github.com/nothings/stb/blob/5736b15f7ea0ffb08dd38af21067c314d6a3aae9/stb_vorbis.c#L3652-L3658
- https://github.com/nothings/stb/blob/5736b15f7ea0ffb08dd38af21067c314d6a3aae9/stb_vorbis.c#L3653
- https://github.com/nothings/stb/blob/5736b15f7ea0ffb08dd38af21067c314d6a3aae9/stb_vorbis.c#L3658
- https://github.com/nothings/stb/blob/5736b15f7ea0ffb08dd38af21067c314d6a3aae9/stb_vorbis.c#L3670C7-L3670C75
- https://github.com/nothings/stb/blob/5736b15f7ea0ffb08dd38af21067c314d6a3aae9/stb_vorbis.c#L950-L961
- https://nvd.nist.gov/vuln/detail/CVE-2023-45677
- https://securitylab.github.com/advisories/GHSL-2023-145_GHSL-2023-151_stb_image_h/
