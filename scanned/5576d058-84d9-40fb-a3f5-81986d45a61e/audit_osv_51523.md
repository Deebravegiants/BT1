# [M] CVE-2021-31317

## Summary
Severity: Medium
Advisory: CVE-2021-31317
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N)
Published: 2021-05-18
Source: https://osv.dev/vulnerability/CVE-2021-31317
Type: osv

## Details
Telegram Android <7.1.0 (2090), Telegram iOS <7.1, and Telegram macOS <7.1 are affected by a Type Confusion in the VDasher constructor of their custom fork of the rlottie library. A remote attacker might be able to access Telegram's heap memory out-of-bounds on a victim device via a malicious animated sticker.

## References
- https://www.shielder.it/advisories/telegram-rlottie-vdasher-vdasher-type-confusion/
- https://www.shielder.it/blog/2021/02/hunting-for-bugs-in-telegrams-animated-stickers-remote-attack-surface/
