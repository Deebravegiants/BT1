# [M] CVE-2016-10351

## Summary
Severity: Medium
Advisory: CVE-2016-10351
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2017-05-01
Source: https://osv.dev/vulnerability/CVE-2016-10351
Type: osv

## Details
Telegram Desktop 0.10.19 uses 0755 permissions for $HOME/.TelegramDesktop, which allows local users to obtain sensitive authentication information via standard filesystem operations.

## References
- https://github.com/telegramdesktop/tdesktop/pull/3842/commits/388703b9ca1912a5438e37f9dd54c35805f2c594
- https://github.com/telegramdesktop/tdesktop/issues/2666
