# [M] Exiv2 has quadratic performance in ICC profile parsing in `JpegBase::readMetadata`

## Summary
Severity: Medium
Advisory: JLSEC-2026-1315
Ecosystem: Julia
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2026-08-13
Source: https://osv.dev/vulnerability/JLSEC-2026-1315
Type: osv

## Affected
- Julia: `Exiv2_jll` — affected unspecified

## Details
### Impact

A denial-of-service was found in Exiv2 version v0.28.5: a quadratic algorithm in the ICC profile parsing code in `jpegBase::readMetadata()` can cause Exiv2 to run for a long time. Exiv2 is a command-line utility and C++ library for reading, writing, deleting, and modifying the metadata of image files. The denial-of-service is triggered when Exiv2 is used to read the metadata of a crafted jpg image file.

### Patches

The bug is fixed in version v0.28.6.

### References

Issue: https://github.com/Exiv2/exiv2/issues/3333
Fixes: https://github.com/Exiv2/exiv2/pull/3335 (main branch), https://github.com/Exiv2/exiv2/pull/3345 (0.28.x branch)

### For more information

Please see our [security policy](https://github.com/Exiv2/exiv2/security/policy) for information about Exiv2 security.

## References
- https://github.com/Exiv2/exiv2/issues/3333
- https://github.com/Exiv2/exiv2/pull/3335
- https://github.com/Exiv2/exiv2/pull/3345
- https://github.com/Exiv2/exiv2/security/advisories/GHSA-m54q-mm9w-fp6g
- https://github.com/advisories/GHSA-m54q-mm9w-fp6g
- https://nvd.nist.gov/vuln/detail/CVE-2025-55304
