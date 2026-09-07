# [M] katello SQL Injection vulnerability

## Summary
Severity: Medium
Advisory: GHSA-jx5v-788g-qw58
CVE: CVE-2018-14623
CWE: CWE-209, CWE-89
Ecosystem: RubyGems
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-jx5v-788g-qw58
Type: github-advisory

## Affected
- RubyGems: `katello` — affected >=0

## Details
A SQL injection flaw was found in katello's errata-related API. An authenticated remote attacker can craft input data to force a malformed SQL query to the backend database, which will leak internal IDs. This is issue is related to an incomplete fix for CVE-2016-3072. Version 3.10 and older is vulnerable.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-14623
- https://access.redhat.com/errata/RHSA-2018:0336
- https://access.redhat.com/security/cve/CVE-2018-14623
- https://bugzilla.redhat.com/show_bug.cgi?id=1623719
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2018-14623
- https://github.com/Katello/katello
- https://github.com/advisories/GHSA-527r-mfmj-prqf
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/katello/CVE-2018-14623.yml
- https://web.archive.org/web/20200227100255/http://www.securityfocus.com/bid/106224
