# [M] Disclosure of uninitialized memory in stbi__tga_load in stb_image

## Summary
Severity: Medium
Advisory: CVE-2023-45663
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2023-10-20
Source: https://osv.dev/vulnerability/CVE-2023-45663
Type: osv

## Details
stb_image is a single file MIT licensed library for processing images. The stbi__getn function reads a specified number of bytes from context (typically a file) into the specified buffer. In case the file stream points to the end, it returns zero. There are two places where its return value is not checked: In the `stbi__hdr_load` function and in the `stbi__tga_load` function. The latter of the two is likely more exploitable as an attacker may also control the size of an uninitialized buffer.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/45xxx/CVE-2023-45663.json
- https://github.com/nothings/stb/blob/5736b15f7ea0ffb08dd38af21067c314d6a3aae9/stb_image.h#L1664
- https://github.com/nothings/stb/blob/5736b15f7ea0ffb08dd38af21067c314d6a3aae9/stb_image.h#L5936C10-L5936C20
- https://github.com/nothings/stb/blob/5736b15f7ea0ffb08dd38af21067c314d6a3aae9/stb_image.h#L7221
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/NMXKOKPP4BKTNUTF5KSRDQAWOUILQZNO/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/QVABVF4GEM6BYD5L4L64RCRSXUHY6LGN/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/UVQ7ONFH5GWLMXYEAJG32A3EUKUCEVCR/
- https://nvd.nist.gov/vuln/detail/CVE-2023-45663
- https://securitylab.github.com/advisories/GHSL-2023-145_GHSL-2023-151_stb_image_h/
