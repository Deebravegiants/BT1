# [H] FedMsg not properly completing message validation

## Summary
Severity: High
Advisory: GHSA-p7xc-35m8-57pr
CVE: CVE-2017-1000001
CWE: CWE-20
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2018-07-13
Source: https://github.com/advisories/GHSA-p7xc-35m8-57pr
Type: github-advisory

## Affected
- PyPI: `FedMsg` — affected >=0 <0.18.2

## Details
FedMsg 0.18.1 and older is vulnerable to a message validation flaw resulting in message validation not being enabled if configured to be on.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-1000001
- https://github.com/advisories/GHSA-p7xc-35m8-57pr
- https://github.com/fedora-infra/fedmsg
- https://github.com/fedora-infra/fedmsg/blob/0.18.2/CHANGELOG.rst
- https://github.com/pypa/advisory-database/tree/main/vulns/fedmsg/PYSEC-2017-13.yaml
