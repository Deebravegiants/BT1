# [H] hammer_cli_foreman Improper Certificate Validation vulnerability

## Summary
Severity: High
Advisory: GHSA-77h8-xr85-3x5q
CVE: CVE-2017-2667
CWE: CWE-295, CWE-345
Ecosystem: RubyGems
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-77h8-xr85-3x5q
Type: github-advisory

## Affected
- RubyGems: `hammer_cli_foreman` — affected >=0 <0.10.0

## Details
Hammer CLI, a CLI utility for Foreman, before version 0.10.0, did not explicitly set the verify_ssl flag for apipie-bindings that disable it by default. As a result the server certificates are not checked and connections are prone to man-in-the-middle attacks.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-2667
- https://access.redhat.com/errata/RHSA-2018:0336
- https://bugzilla.redhat.com/show_bug.cgi?id=1436262
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/hammer_cli_foreman/CVE-2017-2667.yml
- https://github.com/theforeman/hammer-cli-foreman
- https://web.archive.org/web/20200227181720/http://www.securityfocus.com/bid/97153
- http://projects.theforeman.org/issues/19033
- http://www.securityfocus.com/bid/97153
