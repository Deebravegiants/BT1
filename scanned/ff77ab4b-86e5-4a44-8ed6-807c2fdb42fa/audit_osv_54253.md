# [H] Double-free in stbi__load_gif_main_outofmem in stb_image

## Summary
Severity: High
Advisory: CVE-2023-45664
CVSS: 7.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L)
Published: 2023-10-20
Source: https://osv.dev/vulnerability/CVE-2023-45664
Type: osv

## Details
stb_image is a single file MIT licensed library for processing images. A crafted image file can trigger `stbi__load_gif_main_outofmem` attempt to double-free the out variable. This happens in `stbi__load_gif_main` because when the `layers * stride` value is zero the behavior is implementation defined, but common that realloc frees the old memory and returns null pointer. Since it attempts to double-free the memory a few lines below the first “free”, the issue can be potentially exploited only in a multi-threaded environment. In the worst case this may lead to code execution.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/45xxx/CVE-2023-45664.json
- https://github.com/nothings/stb/blob/5736b15f7ea0ffb08dd38af21067c314d6a3aae9/stb_image.h#L6993-L6995
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/NMXKOKPP4BKTNUTF5KSRDQAWOUILQZNO/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/QVABVF4GEM6BYD5L4L64RCRSXUHY6LGN/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/UVQ7ONFH5GWLMXYEAJG32A3EUKUCEVCR/
- https://nvd.nist.gov/vuln/detail/CVE-2023-45664
- https://securitylab.github.com/advisories/GHSL-2023-145_GHSL-2023-151_stb_image_h/
