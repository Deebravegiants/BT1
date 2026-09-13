# [H] CVE-2019-18936

## Summary
Severity: High
Advisory: CVE-2019-18936
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-03-21
Source: https://osv.dev/vulnerability/CVE-2019-18936
Type: osv

## Details
UniValue::read() in UniValue before 1.0.5 allow attackers to cause a denial of service (the class internal data reaches an inconsistent state) via input data that triggers an error.

## References
- https://github.com/jgarzik/univalue/compare/v1.0.4...v1.0.5
- https://github.com/jgarzik/univalue/pull/58
