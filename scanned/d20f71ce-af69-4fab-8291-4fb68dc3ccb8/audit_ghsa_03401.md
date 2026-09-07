# [C] Deserialization of Untrusted Data in PyYAML

## Summary
Severity: Critical
Advisory: GHSA-3pqx-4fqf-j49f
CVE: CVE-2019-20477
CWE: CWE-502
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-04-20
Source: https://github.com/advisories/GHSA-3pqx-4fqf-j49f
Type: github-advisory

## Affected
- PyPI: `pyyaml` — affected >=5.1 <5.2

## Details
PyYAML 5.1 through 5.1.2 has insufficient restrictions on the load and load_all functions because of a class deserialization issue, e.g., Popen is a class in the subprocess module. NOTE: this issue exists because of an incomplete fix for CVE-2017-18342.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-20477
- https://github.com/advisories/GHSA-3pqx-4fqf-j49f
- https://github.com/pypa/advisory-database/tree/main/vulns/pyyaml/PYSEC-2020-176.yaml
- https://github.com/yaml/pyyaml
- https://github.com/yaml/pyyaml/blob/master/CHANGES
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/33VBUY73AA6CTTYL3LRWHNFDULV7PFPN
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/52N5XS73Z5S4ZN7I7R56ICCPCTKCUV4H
- https://www.exploit-db.com/download/47655
