# [M] Flair allows arbitrary code execution

## Summary
Severity: Medium
Advisory: GHSA-9rw2-jf8x-cgwm
CVE: CVE-2024-10073
CWE: CWE-94
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2024-10-17
Source: https://github.com/advisories/GHSA-9rw2-jf8x-cgwm
Type: github-advisory

## Affected
- PyPI: `flair` — affected >=0 <0.15.0

## Details
A vulnerability, which was classified as critical, was found in flairNLP flair 0.14.0. Affected is the function ClusteringModel of the file flair\models\clustering.py of the component Mode File Loader. The manipulation leads to code injection. It is possible to launch the attack remotely. The complexity of an attack is rather high. The exploitability is told to be difficult. The exploit has been disclosed to the public and may be used. The vendor was contacted early about this disclosure but did not respond in any way.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-10073
- https://github.com/flairNLP/flair/commit/fb27c7eb1d92855c27db820a108b17883a5d6fc1
- https://github.com/bayuncao/vul-cve-20
- https://github.com/bayuncao/vul-cve-20/blob/main/PoC.py
- https://github.com/flairNLP/flair
- https://github.com/flairNLP/flair/releases/tag/v0.15.0
- https://vuldb.com/?ctiid.280722
- https://vuldb.com/?id.280722
- https://vuldb.com/?submit.420055
