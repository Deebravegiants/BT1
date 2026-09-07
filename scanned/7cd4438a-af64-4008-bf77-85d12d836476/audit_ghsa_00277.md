# [C] Unsafe deserialization in owlmixin

## Summary
Severity: Critical
Advisory: GHSA-ccmq-qvcp-5mrm
CVE: CVE-2017-16618
CWE: CWE-502
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2018-07-13
Source: https://github.com/advisories/GHSA-ccmq-qvcp-5mrm
Type: github-advisory

## Affected
- PyPI: `owlmixin` — affected >=0 <2.0.0

## Details
An exploitable vulnerability exists in the YAML loading functionality of util.py in OwlMixin before 2.0.0a12. A "Load YAML" string or file (aka load_yaml or load_yamlf) can execute arbitrary Python commands resulting in command execution because load is used where safe_load should have been used. An attacker can insert Python into loaded YAML to trigger this vulnerability.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-16618
- https://github.com/tadashi-aikawa/owlmixin/issues/12
- https://github.com/tadashi-aikawa/owlmixin/commit/5d0575303f6df869a515ced4285f24ba721e0d4e
- https://github.com/advisories/GHSA-ccmq-qvcp-5mrm
- https://github.com/pypa/advisory-database/tree/main/vulns/owlmixin/PYSEC-2017-22.yaml
- https://github.com/tadashi-aikawa/owlmixin
- https://joel-malwarebenchmark.github.io/blog/2017/11/08/cve-2017-16618-convert-through-owlmixin
