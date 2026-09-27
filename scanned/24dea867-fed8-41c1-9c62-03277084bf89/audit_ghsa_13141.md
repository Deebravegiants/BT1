# [H] OpenStack Heat information leak vulnerability

## Summary
Severity: High
Advisory: GHSA-5836-grcc-8j89
CVE: CVE-2023-1625
CWE: CWE-200
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:L/A:L (CVSS_V3)
Published: 2023-09-24
Source: https://github.com/advisories/GHSA-5836-grcc-8j89
Type: github-advisory

## Affected
- PyPI: `openstack-heat` — affected >=0 <20.0.0

## Details
An information leak was discovered in OpenStack heat. This issue could allow a remote, authenticated attacker to use the 'stack show' command to reveal parameters which are supposed to remain hidden. This has a low impact to the confidentiality, integrity, and availability of the system.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-1625
- https://github.com/openstack/heat/commit/a49526c278e52823080c7f3fcb72785b93fd4dcb
- https://access.redhat.com/security/cve/CVE-2023-1625
- https://bugzilla.redhat.com/show_bug.cgi?id=2181621
- https://github.com/openstack/heat
- https://launchpad.net/bugs/1999665
