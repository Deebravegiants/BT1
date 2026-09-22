# [M] Null pointer dereference because of an uninitialized variable in stb_image

## Summary
Severity: Medium
Advisory: CVE-2023-45667
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2023-10-20
Source: https://osv.dev/vulnerability/CVE-2023-45667
Type: osv

## Details
stb_image is a single file MIT licensed library for processing images.

If `stbi__load_gif_main` in `stbi_load_gif_from_memory` fails it returns a null pointer and may keep the `z` variable uninitialized. In case the caller also sets the flip vertically flag, it continues and calls `stbi__vertical_flip_slices` with the null pointer result value and the uninitialized `z` value. This may result in a program crash.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/45xxx/CVE-2023-45667.json
- https://github.com/nothings/stb/blob/5736b15f7ea0ffb08dd38af21067c314d6a3aae9/stb_image.h#L1442-L1454
- https://github.com/nothings/stb/blob/5736b15f7ea0ffb08dd38af21067c314d6a3aae9/stb_image.h#L1448
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/NMXKOKPP4BKTNUTF5KSRDQAWOUILQZNO/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/QVABVF4GEM6BYD5L4L64RCRSXUHY6LGN/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/UVQ7ONFH5GWLMXYEAJG32A3EUKUCEVCR/
- https://nvd.nist.gov/vuln/detail/CVE-2023-45667
- https://securitylab.github.com/advisories/GHSL-2023-145_GHSL-2023-151_stb_image_h/
