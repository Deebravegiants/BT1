# [M] OpenEXR: Unhandled assert abort in HTJ2K decoder via crafted QCD marker (DoS)

## Summary
Severity: Medium
Advisory: CVE-2026-53532
Aliases: GHSA-2f85-52wj-hc3c
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-24
Source: https://osv.dev/vulnerability/CVE-2026-53532
Type: osv

## Details
OpenEXR is the reference implementation and specification for the EXR image format, widely used in the motion picture industry. In versions 3.4.0 through 3.4.12, a crafted HTJ2K-compressed EXR file causes an unconditional process abort in any application that calls exr_start_read() on untrusted input, resulting in denial of service. The crash is triggered by a QCD marker whose lower five bits are zero, which OpenEXR passes into the vendored OpenJPH library while constructing the codestream and evaluating its quantization delta parameters. OpenJPH uses an assertion rather than a recoverable error to validate those bits, so any invalid value calls abort() directly and cannot be intercepted by surrounding error handling, a problem compounded by OpenEXR wrapping only its internal HT header parser in error handling while leaving the later codestream read and construction calls unprotected. This issue has been resolved in version 3.4.13.

## References
- https://github.com/AcademySoftwareFoundation/openexr/releases/tag/v3.4.13
- https://github.com/AcademySoftwareFoundation/openexr/security/advisories/GHSA-2f85-52wj-hc3c
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53532.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-53532
