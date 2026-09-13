# [M] ai-flow Deserialization of Untrusted Data vulnerability

## Summary
Severity: Medium
Advisory: GHSA-7mgg-3rq2-hff4
CVE: CVE-2024-0960
CWE: CWE-502
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2024-01-27
Source: https://github.com/advisories/GHSA-7mgg-3rq2-hff4
Type: github-advisory

## Affected
- PyPI: `ai-flow` — affected >=0

## Details
A vulnerability was found in flink-extended ai-flow 0.3.1. It has been declared as critical. Affected by this vulnerability is the function cloudpickle.loads of the file `\ai_flow\cli\commands\workflow_command.py`. The manipulation leads to deserialization. The attack can be launched remotely. The complexity of an attack is rather high. The exploitation appears to be difficult. The exploit has been disclosed to the public and may be used. The identifier VDB-252205 was assigned to this vulnerability.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-0960
- https://github.com/bayuncao/vul-cve-8
- https://github.com/bayuncao/vul-cve-8/blob/main/dataset.pkl
- https://github.com/flink-extended/ai-flow
- https://vuldb.com/?ctiid.252205
- https://vuldb.com/?id.252205
