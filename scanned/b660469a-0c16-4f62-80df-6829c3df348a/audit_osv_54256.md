# [M] 0 byte write heap buffer overflow in start_decoder in stb_vorbis

## Summary
Severity: Medium
Advisory: CVE-2023-45675
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:L)
Published: 2023-10-20
Source: https://osv.dev/vulnerability/CVE-2023-45675
Type: osv

## Details
stb_vorbis is a single file MIT licensed library for processing ogg vorbis files. A crafted file may trigger out of bounds write in `f->vendor[len] = (char)'\0';`. The root cause is that if the len read in `start_decoder` is `-1` and `len + 1` becomes 0 when passed to `setup_malloc`. The `setup_malloc` behaves differently when `f->alloc.alloc_buffer` is pre-allocated. Instead of returning `NULL` as in `malloc` case it shifts the pre-allocated buffer by zero and returns the currently available memory block. This issue may lead to code execution.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/45xxx/CVE-2023-45675.json
- https://github.com/nothings/stb/blob/5736b15f7ea0ffb08dd38af21067c314d6a3aae9/stb_vorbis.c#L3652-L3658
- https://github.com/nothings/stb/blob/5736b15f7ea0ffb08dd38af21067c314d6a3aae9/stb_vorbis.c#L3658
- https://github.com/nothings/stb/blob/5736b15f7ea0ffb08dd38af21067c314d6a3aae9/stb_vorbis.c#L950-L960
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/NMXKOKPP4BKTNUTF5KSRDQAWOUILQZNO/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/QVABVF4GEM6BYD5L4L64RCRSXUHY6LGN/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/UVQ7ONFH5GWLMXYEAJG32A3EUKUCEVCR/
- https://nvd.nist.gov/vuln/detail/CVE-2023-45675
- https://securitylab.github.com/advisories/GHSL-2023-145_GHSL-2023-151_stb_image_h/
