# [M] tripleo-ansible may disclose important configuration details from an OpenStack deployment

## Summary
Severity: Medium
Advisory: GHSA-7x96-2w32-w3gw
CVE: CVE-2022-3101
CWE: CWE-22, CWE-276, CWE-732
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-03-23
Source: https://github.com/advisories/GHSA-7x96-2w32-w3gw
Type: github-advisory

## Affected
- PyPI: `tripleo-ansible` — affected >=0

## Details
A flaw was found in tripleo-ansible. Due to an insecure default configuration, the permissions of a sensitive file are not sufficiently restricted. This flaw allows a local attacker to use brute force to explore the relevant directory and discover the file, leading to information disclosure of important configuration details from the OpenStack deployment.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-3101
- https://access.redhat.com/security/cve/CVE-2022-3101
- https://github.com/openstack/tripleo-ansible
