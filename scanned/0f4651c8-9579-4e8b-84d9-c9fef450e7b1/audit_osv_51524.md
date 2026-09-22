# [H] CVE-2021-31321

## Summary
Severity: High
Advisory: CVE-2021-31321
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:H)
Published: 2021-05-18
Source: https://osv.dev/vulnerability/CVE-2021-31321
Type: osv

## Details
Telegram Android <7.1.0 (2090), Telegram iOS <7.1, and Telegram macOS <7.1 are affected by a Stack Based Overflow in the gray_split_cubic function of their custom fork of the rlottie library. A remote attacker might be able to overwrite Telegram's stack memory out-of-bounds on a victim device via a malicious animated sticker.

## References
- https://www.shielder.it/advisories/telegram-rlottie-gray_split_cubic-stack-buffer-overflow/
- https://www.shielder.it/blog/2021/02/hunting-for-bugs-in-telegrams-animated-stickers-remote-attack-surface/
