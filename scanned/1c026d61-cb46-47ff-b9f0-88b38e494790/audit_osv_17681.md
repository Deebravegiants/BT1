# [H] CVE-2020-1898

## Summary
Severity: High
Advisory: CVE-2020-1898
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-03-11
Source: https://osv.dev/vulnerability/CVE-2020-1898
Type: osv

## Details
The fb_unserialize function did not impose a depth limit for nested deserialization. That meant a maliciously constructed string could cause deserialization to recurse, leading to stack exhaustion. This issue affected HHVM prior to v4.32.3, between versions 4.33.0 and 4.56.0, 4.57.0, 4.58.0, 4.58.1, 4.59.0, 4.60.0, 4.61.0, 4.62.0.

## References
- https://hhvm.com/blog/2020/06/30/security-update.html
- https://github.com/facebook/hhvm/commit/1746dfb11fc0048366f34669e74318b8278a684c
