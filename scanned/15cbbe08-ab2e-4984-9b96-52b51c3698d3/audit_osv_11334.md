# [M] CVE-2017-7448

## Summary
Severity: Medium
Advisory: CVE-2017-7448
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-04-05
Source: https://osv.dev/vulnerability/CVE-2017-7448
Type: osv

## Details
The allocate_channel_framebuffer function in uncompressed_components.hh in Dropbox Lepton 1.2.1 allows remote attackers to cause a denial of service (divide-by-zero error and application crash) via a malformed JPEG image.

## References
- http://www.securityfocus.com/bid/97490
- https://github.com/dropbox/lepton/commit/7789d99ac156adfd7bbf66e7824bd3e948a74cf7
- https://github.com/dropbox/lepton/issues/86
