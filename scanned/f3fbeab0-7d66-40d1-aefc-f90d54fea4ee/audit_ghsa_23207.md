# [H] Openstack cinder Improper handling of ScaleIO backend credentials

## Summary
Severity: High
Advisory: GHSA-v3m2-pg96-w33m
CVE: CVE-2020-10755
CWE: CWE-522
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-v3m2-pg96-w33m
Type: github-advisory

## Affected
- PyPI: `cinder` — affected >=14.0.0 <14.1.0
- PyPI: `cinder` — affected >=15.0.0 <15.2.0
- PyPI: `cinder` — affected >=16.0.0 <16.1.0
- PyPI: `os-brick` — affected >=2.8.0 <2.8.6
- PyPI: `os-brick` — affected >=2.10.0 <2.10.4
- PyPI: `os-brick` — affected >=3.0.0 <3.0.2

## Details
An insecure-credentials flaw was found in all openstack-cinder versions before openstack-cinder 14.1.0, all openstack-cinder 15.x.x versions before openstack-cinder 15.2.0 and all openstack-cinder 16.x.x versions before openstack-cinder 16.1.0. When using openstack-cinder with the Dell EMC ScaleIO or VxFlex OS backend storage driver, credentials for the entire backend are exposed in the ``connection_info`` element in all Block Storage v3 Attachments API calls containing that element. This flaw enables an end-user to create a volume, make an API call to show the attachment detail information, and retrieve a username and password that may be used to connect to another user's volume. Additionally, these credentials are valid for the ScaleIO or VxFlex OS Management API, should an attacker discover the Management API endpoint. Source: OpenStack project

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-10755
- https://github.com/openstack/cinder/commit/ba785eef5f515b869c0d68016e84bb74f76ab45e
- https://github.com/openstack/os-brick/commit/4047948f1ac8055a025972ad73ec3ec421450775
- https://bugs.launchpad.net/cinder/+bug/1823200
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2020-10755
- https://github.com/pypa/advisory-database/tree/main/vulns/cinder/PYSEC-2020-228.yaml
- https://usn.ubuntu.com/4420-1
- https://wiki.openstack.org/wiki/OSSN/OSSN-0086
