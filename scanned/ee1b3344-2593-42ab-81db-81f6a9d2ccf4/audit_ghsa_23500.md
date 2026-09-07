# [M] OpenStack Horizon Open redirect in workflow forms

## Summary
Severity: Medium
Advisory: GHSA-f8fh-xp28-q59m
CVE: CVE-2020-29565
CWE: CWE-601
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-f8fh-xp28-q59m
Type: github-advisory

## Affected
- PyPI: `horizon` — affected >=0 <15.3.2
- PyPI: `horizon` — affected >=16.0.0 <16.2.1
- PyPI: `horizon` — affected >=17.0.0 <18.3.3
- PyPI: `horizon` — affected >=18.4.0 <18.6.0

## Details
An issue was discovered in OpenStack Horizon before 15.3.2, 16.x before 16.2.1, 17.x and 18.x before 18.3.3, 18.4.x, and 18.5.x. There is a lack of validation of the "next" parameter, which would allow someone to supply a malicious URL in Horizon that can cause an automatic redirect to the provided malicious URL.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-29565
- https://github.com/openstack/horizon/commit/252467100f75587e18df9c43ed5802ee8f0017fa
- https://github.com/openstack/horizon/commit/6c208edf323ced07b15ec4bc3879bddb91d398bc
- https://github.com/openstack/horizon/commit/9e0e333ab5277b6c396f602862ff90398cb0242b
- https://github.com/openstack/horizon/commit/baa370f84332ad41502daea29a551705696f4421
- https://bugs.launchpad.net/horizon/+bug/1865026
- https://github.com/openstack/horizon
- https://github.com/pypa/advisory-database/tree/main/vulns/horizon/PYSEC-2020-45.yaml
- https://review.opendev.org/c/openstack/horizon/+/758841
- https://review.opendev.org/c/openstack/horizon/+/758843
- https://security.openstack.org/ossa/OSSA-2020-008.html
- https://www.debian.org/security/2020/dsa-4820
- http://www.openwall.com/lists/oss-security/2020/12/08/2
