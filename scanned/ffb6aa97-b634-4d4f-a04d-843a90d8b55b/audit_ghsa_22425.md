# [M] openshift-origin-node Improper Input Validation vulnerability

## Summary
Severity: Medium
Advisory: GHSA-756m-3qf2-hp58
CVE: CVE-2014-0084
CWE: CWE-20
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-756m-3qf2-hp58
Type: github-advisory

## Affected
- RubyGems: `openshift-origin-node` — affected >=0

## Details
Ruby gem openshift-origin-node before 2014-02-14 does not contain a cronjob timeout which could result in a denial of service in cron.daily and cron.weekly.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-0084
- https://access.redhat.com/errata/RHBA-2014:0487
- https://access.redhat.com/security/cve/CVE-2014-0084
- https://bugzilla.redhat.com/show_bug.cgi?id=1065198
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2014-0084
- https://github.com/openshift/origin-server
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/openshift-origin-node/CVE-2014-0084.yml
