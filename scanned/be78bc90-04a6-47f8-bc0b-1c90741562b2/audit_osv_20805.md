# [C] CVE-2021-3726

## Summary
Severity: Critical
Advisory: CVE-2021-3726
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-11-30
Source: https://osv.dev/vulnerability/CVE-2021-3726
Type: osv

## Details
# Vulnerability in `title` function **Description**: the `title` function defined in `lib/termsupport.zsh` uses `print` to set the terminal title to a user-supplied string. In Oh My Zsh, this function is always used securely, but custom user code could use the `title` function in a way that is unsafe. **Fixed in**: [a263cdac](https://github.com/ohmyzsh/ohmyzsh/commit/a263cdac). **Impacted areas**: - `title` function in `lib/termsupport.zsh`. - Custom user code using the `title` function.

## References
- https://github.com/ohmyzsh/ohmyzsh/commit/a263cdac
