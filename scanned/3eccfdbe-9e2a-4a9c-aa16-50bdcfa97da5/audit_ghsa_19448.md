# [M] InternLM LMDeploy code injection vulnerability

## Summary
Severity: Medium
Advisory: GHSA-jfvg-qm4p-473x
CVE: CVE-2025-3163
CWE: CWE-74, CWE-94
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2025-04-03
Source: https://github.com/advisories/GHSA-jfvg-qm4p-473x
Type: github-advisory

## Affected
- PyPI: `lmdeploy` — affected >=0

## Details
A vulnerability was found in InternLM LMDeploy up to 0.7.1. It has been declared as critical. Affected by this vulnerability is the function Open of the file lmdeploy/docs/en/conf.py. The manipulation leads to code injection. It is possible to launch the attack on the local host. The exploit has been disclosed to the public and may be used.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-3163
- https://github.com/InternLM/lmdeploy/issues/3254
- https://github.com/InternLM/lmdeploy/issues/3254#issue-2918865448
- https://github.com/InternLM/lmdeploy
- https://vuldb.com/?ctiid.303109
- https://vuldb.com/?id.303109
- https://vuldb.com/?submit.542527
