# [H] CVE-2020-10184

## Summary
Severity: High
Advisory: CVE-2020-10184
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-03-05
Source: https://osv.dev/vulnerability/CVE-2020-10184
Type: osv

## Details
The verify endpoint in YubiKey Validation Server before 2.40 does not check the length of SQL queries, which allows remote attackers to cause a denial of service, aka SQL injection. NOTE: this issue is potentially relevant to persons outside Yubico who operate a self-hosted OTP validation service; the issue does NOT affect YubiCloud.

## References
- https://lists.debian.org/debian-lts-announce/2020/03/msg00014.html
- https://github.com/Yubico/yubikey-val/releases/tag/yubikey-val-2.40
- https://www.yubico.com/support/security-advisories/ysa-2020-01/
