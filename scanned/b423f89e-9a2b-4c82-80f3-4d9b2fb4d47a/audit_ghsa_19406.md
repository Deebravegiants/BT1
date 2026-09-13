# [M] LMDeploy Improper Input Validation Vulnerability

## Summary
Severity: Medium
Advisory: GHSA-7vc5-mjwp-c8fq
CVE: CVE-2025-3162
CWE: CWE-20, CWE-502
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2025-04-03
Source: https://github.com/advisories/GHSA-7vc5-mjwp-c8fq
Type: github-advisory

## Affected
- PyPI: `lmdeploy` — affected >=0

## Details
A vulnerability was found in InternLM LMDeploy up to 0.7.1. It has been classified as critical. Affected is the function load_weight_ckpt of the file lmdeploy/lmdeploy/vl/model/utils.py of the component PT File Handler. The manipulation leads to deserialization. Attacking locally is a requirement. The exploit has been disclosed to the public and may be used.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-3162
- https://github.com/InternLM/lmdeploy/issues/3255
- https://github.com/InternLM/lmdeploy/issues/3255#issue-2918985270
- https://github.com/InternLM/lmdeploy
- https://vuldb.com/?ctiid.303108
- https://vuldb.com/?id.303108
- https://vuldb.com/?submit.542520
