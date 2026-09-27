# [C] smart_proxy_dynflow gem authentication bypass in Foreman remote execution feature

## Summary
Severity: Critical
Advisory: GHSA-gx5g-xcxj-cx2w
CVE: CVE-2018-14643
CWE: CWE-287
Ecosystem: RubyGems
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2018-10-08
Source: https://github.com/advisories/GHSA-gx5g-xcxj-cx2w
Type: github-advisory

## Affected
- RubyGems: `smart_proxy_dynflow` — affected >=0.2.0 <0.2.1
- RubyGems: `smart_proxy_dynflow` — affected >=0 <0.1.11

## Details
An authentication bypass flaw was found in the smart_proxy_dynflow component used by Foreman. A malicious attacker can use this flaw to remotely execute arbitrary commands on machines managed by vulnerable Foreman instances, in a highly privileged context.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-14643
- https://github.com/theforeman/smart_proxy_dynflow/pull/54
- https://access.redhat.com/errata/RHSA-2018:2733
- https://access.redhat.com/security/cve/CVE-2018-14643
- https://bugzilla.redhat.com/show_bug.cgi?id=1629063
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2018-14643
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/smart_proxy_dynflow/CVE-2018-14643.yml
- https://github.com/theforeman/smart_proxy_dynflow
