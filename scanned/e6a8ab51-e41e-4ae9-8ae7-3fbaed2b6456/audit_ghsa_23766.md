# [H] Katello SQL Injection vulnerabilities

## Summary
Severity: High
Advisory: GHSA-527r-mfmj-prqf
CVE: CVE-2016-3072
CWE: CWE-89
Ecosystem: RubyGems
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-527r-mfmj-prqf
Type: github-advisory

## Affected
- RubyGems: `katello` — affected >=0 <2.4.3

## Details
Multiple SQL injection vulnerabilities in the scoped_search function in app/controllers/katello/api/v2/api_controller.rb in Katello allow remote authenticated users to execute arbitrary SQL commands via the (1) sort_by or (2) sort_order parameter.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-3072
- https://github.com/Katello/katello/pull/6051
- https://github.com/Katello/katello/commit/5645ed4365980a34e30a9c57fe0793dff729e8e4
- https://access.redhat.com/errata/RHSA-2016:1083
- https://access.redhat.com/security/cve/CVE-2016-3072
- https://bugzilla.redhat.com/show_bug.cgi?id=1322050
- https://github.com/Katello/katello
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/katello/CVE-2016-3072.yml
