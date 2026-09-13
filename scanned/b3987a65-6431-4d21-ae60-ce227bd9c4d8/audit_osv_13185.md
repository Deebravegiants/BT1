# [H] CVE-2018-18444

## Summary
Severity: High
Advisory: CVE-2018-18444
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-10-17
Source: https://osv.dev/vulnerability/CVE-2018-18444
Type: osv

## Details
makeMultiView.cpp in exrmultiview in OpenEXR 2.3.0 has an out-of-bounds write, leading to an assertion failure or possibly unspecified other impact.

## References
- https://github.com/openexr/openexr/releases/tag/v2.4.0
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/5E2OZU4ZSF5W4ODBU4L547HX5A4WOBFV/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/IZN7WUH3SR6DSRODRB4SLFTBKP74FVC5/
- https://usn.ubuntu.com/4148-1/
- https://usn.ubuntu.com/4339-1/
- https://github.com/openexr/openexr/issues/351
