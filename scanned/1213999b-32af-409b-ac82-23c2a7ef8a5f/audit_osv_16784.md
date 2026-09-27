# [H] CVE-2019-9734

## Summary
Severity: High
Advisory: CVE-2019-9734
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2019-04-24
Source: https://osv.dev/vulnerability/CVE-2019-9734
Type: osv

## Details
Aquarius CMS through 4.3.5 writes POST and GET parameters (including passwords) to a log file due to an overwriting of configuration parameters under certain circumstances.

## References
- https://github.com/aquaverde/aquarius-core/commit/d1dfa5b8280388a0b6f2f341f0681522dbea03b0
- https://www.tryption.ch/2019/04/19/cve-2019-9734-password-leakage-im-aquarius-cms/
