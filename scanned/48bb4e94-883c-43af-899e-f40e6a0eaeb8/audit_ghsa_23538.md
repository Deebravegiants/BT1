# [M] OpenStack Identity (Keystone) allows remote attackers to bypass intended access restrictions via revoked PKI token

## Summary
Severity: Medium
Advisory: GHSA-5qpp-v56f-mqfm
CVE: CVE-2013-4294
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-5qpp-v56f-mqfm
Type: github-advisory

## Affected
- PyPI: `keystone` — affected >=2012.2.0 <2013.1.4

## Details
The (1) mamcache and (2) KVS token backends in OpenStack Identity (Keystone) Folsom 2012.2.x and Grizzly before 2013.1.4 do not properly compare the PKI token revocation list with PKI tokens, which allow remote attackers to bypass intended access restrictions via a revoked PKI token.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2013-4294
- https://access.redhat.com/errata/RHSA-2013:1285
- https://access.redhat.com/security/cve/CVE-2013-4294
- https://bugs.launchpad.net/keystone/+bug/1202952
- https://bugzilla.redhat.com/show_bug.cgi?id=1004452
- https://github.com/pypa/advisory-database/tree/main/vulns/keystone/PYSEC-2013-42.yaml
- https://opendev.org/openstack/keystone
- http://rhn.redhat.com/errata/RHSA-2013-1285.html
- http://seclists.org/oss-sec/2013/q3/586
- http://www.ubuntu.com/usn/USN-2002-1
