# [M] OpenStack Sushy-Tools and VirtualBMC Improper Preservation of Permissions

## Summary
Severity: Medium
Advisory: GHSA-5pj3-6fqm-8m7m
CVE: CVE-2022-44020
CWE: CWE-281
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-10-30
Source: https://github.com/advisories/GHSA-5pj3-6fqm-8m7m
Type: github-advisory

## Affected
- PyPI: `sushy-tools` — affected >=0 <0.21.1
- PyPI: `virtualbmc` — affected >=0 <3.0.0

## Details
An issue was discovered in OpenStack Sushy-Tools through 0.21.0 and VirtualBMC through 2.2.2. Changing the boot device configuration with these packages removes password protection from the managed libvirt XML domain. NOTE: this only affects an "unsupported, production-like configuration."

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-44020
- https://github.com/umago/virtualbmc
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/GAD7QJIUWPCKJIGYP7PPHH5DILOEONFE
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/KEQVJF3OQGSDCSQTQQSC54JEGLMSNB4Q
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/QMSUGS4B6EBRHBJMTRXL5RIKJTZTEMJC
- https://review.opendev.org/c/openstack/sushy-tools/+/862625
- https://review.opendev.org/c/openstack/virtualbmc/+/862620
- https://storyboard.openstack.org/#!/story/2010382
