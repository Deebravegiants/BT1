# [M] Ansible Community General Collection is vulnerable to exposure of sensitive information

## Summary
Severity: Medium
Advisory: GHSA-8ggh-xwr9-3373
CVE: CVE-2025-14010
CWE: CWE-200, CWE-532
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2025-12-04
Source: https://github.com/advisories/GHSA-8ggh-xwr9-3373
Type: github-advisory

## Affected
- PyPI: `ansible` — affected >=0 <12.2.0

## Details
A flaw was found in ansible-collection-community-general. This vulnerability allows for information exposure (IE) of sensitive credentials, specifically plaintext passwords, via verbose output when running Ansible with debug modes. Attackers with access to logs could retrieve these secrets and potentially compromise Keycloak accounts or administrative access.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-14010
- https://github.com/ansible-collections/community.general/issues/11000
- https://github.com/ansible-collections/community.general/commit/08e56bbb9b57740a879d3057d84cdb02a162b840
- https://access.redhat.com/security/cve/CVE-2025-14010
- https://bugzilla.redhat.com/show_bug.cgi?id=2418774
- https://github.com/ansible-collections/community.general
- https://github.com/ansible-community/ansible-build-data/blob/12.2.0/12/CHANGELOG-v12.md#security-fixes
