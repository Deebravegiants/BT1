# [H] Code injection in ansible

## Summary
Severity: High
Advisory: GHSA-c2w9-48qc-qpj4
CVE: CVE-2017-2809
CWE: CWE-94
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2018-07-13
Source: https://github.com/advisories/GHSA-c2w9-48qc-qpj4
Type: github-advisory

## Affected
- PyPI: `ansible-vault` — affected >=0 <1.0.5

## Details
An exploitable vulnerability exists in the yaml loading functionality of ansible-vault before 1.0.5. A specially crafted vault can execute arbitrary python commands resulting in command execution. An attacker can insert python into the vault to trigger this vulnerability.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-2809
- https://github.com/tomoh1r/ansible-vault/issues/4
- https://github.com/tomoh1r/ansible-vault/commit/3f8f659ef443ab870bb19f95d43543470168ae04
- https://github.com/advisories/GHSA-c2w9-48qc-qpj4
- https://github.com/pypa/advisory-database/tree/main/vulns/ansible-vault/PYSEC-2017-5.yaml
- https://github.com/tomoh1r/ansible-vault
- https://github.com/tomoh1r/ansible-vault/blob/v1.0.5/CHANGES.txt
- https://web.archive.org/web/20171206173637/http://www.securityfocus.com/bid/100824
- https://www.talosintelligence.com/vulnerability_reports/TALOS-2017-0305
