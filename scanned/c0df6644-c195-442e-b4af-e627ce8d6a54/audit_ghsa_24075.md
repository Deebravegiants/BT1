# [H] OpenStack Identity (Keystone) Multiple vulnerabilities in revocation events

## Summary
Severity: High
Advisory: GHSA-gmvp-5rf9-mxcm
CVE: CVE-2014-5251
CWE: CWE-613
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-gmvp-5rf9-mxcm
Type: github-advisory

## Affected
- PyPI: `keystone` — affected >=0 <8.0.0a0

## Details
The MySQL token driver in OpenStack Identity (Keystone) 2014.1.x before 2014.1.2.1 and Juno before Juno-3 stores timestamps with the incorrect precision, which causes the expiration comparison for tokens to fail and allows remote authenticated users to retain access via an expired token.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-5251
- https://github.com/openstack/keystone/commit/6cbf835542d62e6e5db4b4aef7141b1731cad9dc
- https://github.com/openstack/keystone/commit/7aee6304f653475a4130dc3e5be602e91481f108
- https://bugs.launchpad.net/keystone/+bug/1347961
- https://github.com/openstack/keystone
- https://github.com/pypa/advisory-database/tree/main/vulns/keystone/PYSEC-2014-107.yaml
- http://rhn.redhat.com/errata/RHSA-2014-1121.html
- http://rhn.redhat.com/errata/RHSA-2014-1122.html
- http://www.openwall.com/lists/oss-security/2014/08/15/6
- http://www.ubuntu.com/usn/USN-2324-1
