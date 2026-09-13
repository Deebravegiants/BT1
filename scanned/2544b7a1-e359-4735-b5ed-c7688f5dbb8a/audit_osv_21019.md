# [H] CVE-2021-3962

## Summary
Severity: High
Advisory: CVE-2021-3962
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2021-11-19
Source: https://osv.dev/vulnerability/CVE-2021-3962
Type: osv

## Details
A flaw was found in ImageMagick where it did not properly sanitize certain input before using it to invoke convert processes. This flaw allows an attacker to create a specially crafted image that leads to a use-after-free vulnerability when processed by ImageMagick. The highest threat from this vulnerability is to confidentiality, integrity, as well as system availability.

## References
- https://github.com/ImageMagick/ImageMagick/issues/4446
- https://bugzilla.redhat.com/show_bug.cgi?id=2023196
- https://github.com/ImageMagick/ImageMagick/commit/82775af03bbb10a0a1d0e15c0156c75673b4525e
