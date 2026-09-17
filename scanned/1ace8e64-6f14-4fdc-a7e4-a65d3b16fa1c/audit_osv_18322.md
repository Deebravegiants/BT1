# [H] CVE-2020-26163

## Summary
Severity: High
Advisory: CVE-2020-26163
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2020-09-30
Source: https://osv.dev/vulnerability/CVE-2020-26163
Type: osv

## Details
BigBlueButton Greenlight before 2.5.6 allows HTTP header (Host and Origin) attacks, which can result in Account Takeover if a victim follows a spoofed password-reset link.

## References
- https://github.com/bigbluebutton/greenlight/releases/tag/release-2.5.6
- https://github.com/bigbluebutton/greenlight/pull/1543
- https://www.sakshamanand.com/host-header-injection-bigbluebutton/
