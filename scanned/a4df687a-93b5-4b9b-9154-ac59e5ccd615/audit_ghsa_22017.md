# [H] OpenStack Identity (Keystone) DoS through V3 API authentication chaining

## Summary
Severity: High
Advisory: GHSA-6mv3-p2gr-wgqf
CVE: CVE-2014-2828
CWE: CWE-287
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-6mv3-p2gr-wgqf
Type: github-advisory

## Affected
- PyPI: `keystone` — affected >=0 <8.0.0a0

## Details
The V3 API in OpenStack Identity (Keystone) 2013.1 before 2013.2.4 and icehouse before icehouse-rc2 allows remote attackers to cause a denial of service (CPU consumption) via a large number of the same authentication method in a request, aka "authentication chaining."

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-2828
- https://github.com/openstack/keystone/commit/ce6cedb30c5c4b4cf4db9380f09443de22414b39
- https://github.com/openstack/keystone/commit/e364ba5b12de8e4c11bd80bcca903f9615dcfc2e
- https://github.com/openstack/keystone/commit/ef868ad92c00e23a4a5e9eb71e3e0bf5ae2fff0c
- https://bugs.launchpad.net/keystone/+bug/1300274
- https://github.com/openstack/keystone
- https://github.com/pypa/advisory-database/tree/main/vulns/keystone/PYSEC-2014-106.yaml
- http://rhn.redhat.com/errata/RHSA-2014-1688.html
- http://www.openwall.com/lists/oss-security/2014/04/10/20
