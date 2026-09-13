# [C] CVE-2021-3727

## Summary
Severity: Critical
Advisory: CVE-2021-3727
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-11-30
Source: https://osv.dev/vulnerability/CVE-2021-3727
Type: osv

## Details
# Vulnerability in `rand-quote` and `hitokoto` plugins **Description**: the `rand-quote` and `hitokoto` fetch quotes from quotationspage.com and hitokoto.cn respectively, do some process on them and then use `print -P` to print them. If these quotes contained the proper symbols, they could trigger command injection. Given that they're an external API, it's not possible to know if the quotes are safe to use. **Fixed in**: [72928432](https://github.com/ohmyzsh/ohmyzsh/commit/72928432). **Impacted areas**: - `rand-quote` plugin (`quote` function). - `hitokoto` plugin (`hitokoto` function).

## References
- https://github.com/ohmyzsh/ohmyzsh/commit/72928432
