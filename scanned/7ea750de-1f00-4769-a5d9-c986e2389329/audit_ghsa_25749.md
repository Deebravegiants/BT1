# [M] Exposure of Sensitive Information to an Unauthorized Actor in OpenStack tripleo-heat-templates

## Summary
Severity: Medium
Advisory: GHSA-hm3x-jwwf-jpr9
CVE: CVE-2021-4180
CWE: CWE-200, CWE-668
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-03-24
Source: https://github.com/advisories/GHSA-hm3x-jwwf-jpr9
Type: github-advisory

## Affected
- PyPI: `tripleo-heat-templates` — affected >=0 <11.6.1

## Details
An information exposure flaw in openstack-tripleo-heat-templates allows an external user to discover the internal IP or hostname. An attacker could exploit this by checking the `www_authenticate_uri parameter` (which is visible to all end users) in configuration files. This would give sensitive information which may aid in additional system exploitation. A patch is available on the `master` branch and anticipated to be part of version 11.6.1.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-4180
- https://github.com/openstack/tripleo-heat-templates/commit/160936df134a471cfd245bd60964046027a571ea
- https://github.com/openstack/tripleo-heat-templates/commit/2b9461e97fc5c4ceb0848d1cc4484f656bb85515
- https://bugs.launchpad.net/tripleo/+bug/1955397
- https://bugzilla.redhat.com/show_bug.cgi?id=2035793
- https://github.com/openstack/tripleo-heat-templates
