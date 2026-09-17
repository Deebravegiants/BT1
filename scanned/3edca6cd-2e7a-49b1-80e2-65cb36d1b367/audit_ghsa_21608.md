# [M] Exposure of Resource to Wrong Sphere in ezsystems/ezplatform-kernel

## Summary
Severity: Medium
Advisory: GHSA-x8xx-x82q-42q3
CVE: CVE-2022-25336
CWE: CWE-668
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-02-19
Source: https://github.com/advisories/GHSA-x8xx-x82q-42q3
Type: github-advisory

## Affected
- Packagist: `ezsystems/ezplatform-kernel` — affected >=1.3.0 <1.3.12

## Details
When image files are uploaded, they are made accessible under a name similar to the original file name. There are two issues with this. Both require access to uploading images in order to exploit them, this limits the impact. The first issue is that certain injection attacks can be possible, since not all possible attack vectors are removed from the original file name.

The second issue is that direct access to the images is not access controlled. This is by design, for performance reasons, and documented as such. But it does mean that images not meant to be publicly accessible can be accessed, provided that the image path and filename is correctly deduced and/or guessed, through dictionary attacks and similar.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-25336
- https://developers.ibexa.co/security-advisories/ibexa-sa-2022-001-image-filenames-sanitization
- https://github.com/ezsystems/ezplatform-kernel
