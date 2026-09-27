# [H] OpenStack Nova DoS by rebuilding the same instance with a new image multiple times

## Summary
Severity: High
Advisory: GHSA-vq76-rxx3-4r4r
CVE: CVE-2017-17051
CWE: CWE-400
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:C/C:N/I:N/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-vq76-rxx3-4r4r
Type: github-advisory

## Affected
- PyPI: `nova` — affected >=0 <16.0.4

## Details
An issue was discovered in the default FilterScheduler in OpenStack Nova 16.0.3. By repeatedly rebuilding an instance with new images, an authenticated user may consume untracked resources on a hypervisor host leading to a denial of service, aka doubled resource allocations. This regression was introduced with the fix for OSSA-2017-005 (CVE-2017-16239); however, only Nova stable/pike or later deployments with that fix applied and relying on the default FilterScheduler are affected.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-17051
- https://github.com/openstack/nova/commit/25a1d78e83065c5bea5d8e0a017fd9d0914d41d9
- https://github.com/openstack/nova/commit/fed660c1189fdf4159d97badfdc8c5b35ad14f23
- https://github.com/openstack/nova
- https://launchpad.net/bugs/1732976
- https://review.openstack.org/521662
- https://review.openstack.org/523214
- https://security.openstack.org/ossa/OSSA-2017-006.html
- http://www.securityfocus.com/bid/102102
