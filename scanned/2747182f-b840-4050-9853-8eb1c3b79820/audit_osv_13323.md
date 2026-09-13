# [M] CVE-2018-19218

## Summary
Severity: Medium
Advisory: CVE-2018-19218
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-11-12
Source: https://osv.dev/vulnerability/CVE-2018-19218
Type: osv

## Details
In LibSass 3.5-stable, there is an illegal address access at Sass::Parser::parse_css_variable_value_token that will lead to a DoS attack.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=1643758
