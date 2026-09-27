# [M] Multi-byte read heap buffer overflow in stbi__vertical_flip in stb_image

## Summary
Severity: Medium
Advisory: CVE-2023-45662
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:L)
Published: 2023-10-20
Source: https://osv.dev/vulnerability/CVE-2023-45662
Type: osv

## Details
stb_image is a single file MIT licensed library for processing images. When `stbi_set_flip_vertically_on_load` is set to `TRUE` and `req_comp` is set to a number that doesn’t match the real number of components per pixel, the library attempts to flip the image vertically. A crafted image file can trigger `memcpy` out-of-bounds read because `bytes_per_pixel` used to calculate `bytes_per_row` doesn’t match the real image array dimensions.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/45xxx/CVE-2023-45662.json
- https://github.com/nothings/stb/blob/5736b15f7ea0ffb08dd38af21067c314d6a3aae9/stb_image.h#L1235
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/NMXKOKPP4BKTNUTF5KSRDQAWOUILQZNO/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/QVABVF4GEM6BYD5L4L64RCRSXUHY6LGN/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/UVQ7ONFH5GWLMXYEAJG32A3EUKUCEVCR/
- https://nvd.nist.gov/vuln/detail/CVE-2023-45662
- https://securitylab.github.com/advisories/GHSL-2023-145_GHSL-2023-151_stb_image_h/
