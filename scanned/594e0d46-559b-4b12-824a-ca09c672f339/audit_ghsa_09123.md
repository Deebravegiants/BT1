# [H] Snorkel MultitaskClassifier.load uses an unsafe torch.load

## Summary
Severity: High
Advisory: GHSA-gpx5-7xm4-229w
CVE: CVE-2026-31224
CWE: CWE-502
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-05-12
Source: https://github.com/advisories/GHSA-gpx5-7xm4-229w
Type: github-advisory

## Affected
- PyPI: `snorkel` — affected >=0

## Details
The snorkel library thru v0.10.0 contains an insecure deserialization vulnerability (CWE-502) in the MultitaskClassifier.load() method of the MultitaskClassifier class. The method loads model weight files using torch.load() without enabling the security-restrictive weights_only=True parameter. This default behavior allows the deserialization of arbitrary Python objects via the Pickle module. A remote attacker can exploit this by providing a maliciously crafted model file, leading to arbitrary code execution on the victim's system when the file is loaded via the vulnerable method.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-31224
- https://github.com/snorkel-team/snorkel
- https://www.notion.so/CVE-2026-31224-35d1e1393188814185f3f6db86c9a4e9
