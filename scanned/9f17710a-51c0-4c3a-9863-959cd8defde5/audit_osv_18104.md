# [C] CVE-2020-24074

## Summary
Severity: Critical
Advisory: CVE-2020-24074
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-09-09
Source: https://osv.dev/vulnerability/CVE-2020-24074
Type: osv

## Details
The decode program in silk-v3-decoder Version:20160922 Build By kn007 does not strictly check data, resulting in a buffer overflow.

## References
- https://github.com/kn007/silk-v3-decoder/commit/d216599502662db01c07cc0dfd95ff1f1eaaea02
- https://github.com/kn007/silk-v3-decoder/issues/62
