# [M] OpenStack Keystone Denial of Service vulnerability via a large HTTP request

## Summary
Severity: Medium
Advisory: GHSA-4ppj-4p4v-jf4p
CVE: CVE-2013-0270
CWE: CWE-119, CWE-1284
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-05-05
Source: https://github.com/advisories/GHSA-4ppj-4p4v-jf4p
Type: github-advisory

## Affected
- PyPI: `keystone` — affected >=0 <8.0.0a0

## Details
OpenStack Keystone Grizzly before 2013.1, Folsom, and possibly earlier allows remote attackers to cause a denial of service (CPU and memory consumption) via a large HTTP request, as demonstrated by a long tenant_name when requesting a token.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2013-0270
- https://github.com/openstack/keystone/commit/7691276b869a86c2b75631d5bede9f61e030d9d8
- https://github.com/openstack/keystone/commit/82c87e5638ebaf9f166a9b07a0155291276d6fdc
- https://access.redhat.com/security/cve/CVE-2013-0270
- https://bugs.launchpad.net/keystone/+bug/1099025
- https://bugzilla.redhat.com/show_bug.cgi?id=909012
- https://launchpad.net/keystone/grizzly/2013.1
- http://rhn.redhat.com/errata/RHSA-2013-0708.html
