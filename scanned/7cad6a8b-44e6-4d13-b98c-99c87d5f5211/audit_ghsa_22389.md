# [H] OpenStack Identity (Keystone) Trustee token revocations does not work with memcache backend

## Summary
Severity: High
Advisory: GHSA-23x9-8hxr-978c
CVE: CVE-2014-2237
CWE: CWE-1270, CWE-287
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-23x9-8hxr-978c
Type: github-advisory

## Affected
- PyPI: `keystone` — affected >=0 <8.0.0a0

## Details
The memcache token backend in OpenStack Identity (Keystone) 2013.1 through 2.013.1.4, 2013.2 through 2013.2.2, and icehouse before icehouse-3, when issuing a trust token with impersonation enabled, does not include this token in the trustee's token-index-list, which prevents the token from being invalidated by bulk token revocation and allows the trustee to bypass intended access restrictions.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-2237
- https://github.com/openstack/keystone/commit/813d1254eb4f7a7d40009b23bbadbc4c5cc5daac
- https://github.com/openstack/keystone/commit/a411c944af78c36f2fdb87d305ba452dc52d7ed3
- https://github.com/openstack/keystone/commit/b6f0e26da0e2ab0892a5658da281a065e668637b
- https://bugs.launchpad.net/keystone/+bug/1260080
- https://github.com/openstack/keystone
- https://github.com/pypa/advisory-database/tree/main/vulns/keystone/PYSEC-2014-105.yaml
- https://rhn.redhat.com/errata/RHSA-2014-0580.html
- http://www.openwall.com/lists/oss-security/2014/03/04/16
