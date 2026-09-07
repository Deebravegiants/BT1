# [H] OpenStack Storlets arbitrary code execution vulnerability

## Summary
Severity: High
Advisory: GHSA-rfm2-f94j-qhjp
CVE: CVE-2024-28717
CWE: CWE-367, CWE-400
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-04-22
Source: https://github.com/advisories/GHSA-rfm2-f94j-qhjp
Type: github-advisory

## Affected
- PyPI: `storlets` — affected >=0 <13.0.0.0rc1

## Details
An issue in OpenStack Storlets yoga-eom allows a remote attacker to execute arbitrary code via the gateway.py component.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-28717
- https://github.com/openstack/storlets/commit/5ad58804af885db3eb7a78bea5000c401eeeb70e
- https://bugs.launchpad.net/storlets/+bug/2047723
- https://gist.github.com/Fewword/f098d8d6375ac25e27b18c0e57be532f
- https://github.com/openstack/storlets
