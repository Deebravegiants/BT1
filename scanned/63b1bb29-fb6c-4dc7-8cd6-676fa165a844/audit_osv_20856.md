# [C] CVE-2021-3769

## Summary
Severity: Critical
Advisory: CVE-2021-3769
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-11-30
Source: https://osv.dev/vulnerability/CVE-2021-3769
Type: osv

## Details
# Vulnerability in `pygmalion`, `pygmalion-virtualenv` and `refined` themes **Description**: these themes use `print -P` on user-supplied strings to print them to the terminal. All of them do that on git information, particularly the branch name, so if the branch has a specially-crafted name the vulnerability can be exploited. **Fixed in**: [b3ba9978](https://github.com/ohmyzsh/ohmyzsh/commit/b3ba9978). **Impacted areas**: - `pygmalion` theme. - `pygmalion-virtualenv` theme. - `refined` theme.

## References
- https://github.com/ohmyzsh/ohmyzsh/commit/b3ba9978
