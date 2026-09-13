# [H] CVE-2020-10185

## Summary
Severity: High
Advisory: CVE-2020-10185
CVSS: 8.6 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:H)
Published: 2020-03-05
Source: https://osv.dev/vulnerability/CVE-2020-10185
Type: osv

## Details
The sync endpoint in YubiKey Validation Server before 2.40 allows remote attackers to replay an OTP. NOTE: this issue is potentially relevant to persons outside Yubico who operate a self-hosted OTP validation service with a non-default configuration such as an open sync pool; the issue does NOT affect YubiCloud.

## References
- https://lists.debian.org/debian-lts-announce/2020/03/msg00014.html
- https://github.com/Yubico/yubikey-val/releases/tag/yubikey-val-2.40
- https://www.yubico.com/support/security-advisories/ysa-2020-01/
