# [M] OpenStack Identity Keystone Exposure of Sensitive Information

## Summary
Severity: Medium
Advisory: GHSA-8v8f-vc72-pmhc
CVE: CVE-2014-3621
CWE: CWE-200
Ecosystem: PyPI
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-8v8f-vc72-pmhc
Type: github-advisory

## Affected
- PyPI: `keystone` — affected >=0 <8.0.0a0

## Details
The catalog url replacement in OpenStack Identity (Keystone) before 2013.2.3 and 2014.1 before 2014.1.2.1 allows remote authenticated users to read sensitive configuration options via a crafted endpoint, as demonstrated by "$(admin_token)" in the publicurl endpoint field.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-3621
- https://github.com/openstack/keystone/commit/2989ff257e4fde6a168e25b926805e700406aa80
- https://github.com/openstack/keystone/commit/52714633c9a4dae5e60279217090859aa6dbcb4f
- https://access.redhat.com/errata/RHSA-2014:1688
- https://access.redhat.com/errata/RHSA-2014:1789
- https://access.redhat.com/errata/RHSA-2014:1790
- https://access.redhat.com/security/cve/CVE-2014-3621
- https://bugs.launchpad.net/keystone/+bug/1354208
- https://bugzilla.redhat.com/show_bug.cgi?id=1139937
- http://rhn.redhat.com/errata/RHSA-2014-1688.html
- http://rhn.redhat.com/errata/RHSA-2014-1789.html
- http://rhn.redhat.com/errata/RHSA-2014-1790.html
- http://www.openwall.com/lists/oss-security/2014/09/16/10
- http://www.ubuntu.com/usn/USN-2406-1
