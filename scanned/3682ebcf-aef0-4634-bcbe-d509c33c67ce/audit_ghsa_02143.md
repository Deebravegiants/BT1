# [H] Command injection in Yamale

## Summary
Severity: High
Advisory: GHSA-435p-f82x-mxwm
CVE: CVE-2021-38305
CWE: CWE-434, CWE-78
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-08-11
Source: https://github.com/advisories/GHSA-435p-f82x-mxwm
Type: github-advisory

## Affected
- PyPI: `yamale` — affected >=0 <3.0.8

## Details
23andMe Yamale before 3.0.8 allows remote attackers to execute arbitrary code via a crafted schema file. The schema parser uses eval as part of its processing, and tries to protect from malicious expressions by limiting the builtins that are passed to the eval. When processing the schema, each line is run through Python's eval function to make the validator available. A well-constructed string within the schema rules can execute system commands; thus, by exploiting the vulnerability, an attacker can run arbitrary code on the image that invokes Yamale.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-38305
- https://github.com/23andMe/Yamale/pull/165
- https://github.com/23andMe/Yamale
- https://github.com/23andMe/Yamale/releases/tag/3.0.8
- https://github.com/pypa/advisory-database/tree/main/vulns/yamale/PYSEC-2021-119.yaml
