# [H] Snorkel Trainer.load uses an unsafe torch.load

## Summary
Severity: High
Advisory: GHSA-78cp-f66x-qmh5
CVE: CVE-2026-31222
CWE: CWE-502
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-05-12
Source: https://github.com/advisories/GHSA-78cp-f66x-qmh5
Type: github-advisory

## Affected
- PyPI: `snorkel` — affected >=0

## Details
The snorkel library thru v0.10.0 contains an insecure deserialization vulnerability (CWE-502) in the Trainer.load() method of the Trainer class. The method loads model checkpoint files using torch.load() without enabling the security-restrictive weights_only=True parameter. This default behavior allows the deserialization of arbitrary Python objects via the Pickle module. A remote attacker can exploit this by providing a maliciously crafted model file, leading to arbitrary code execution on the victim's system when the file is loaded via the vulnerable method.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-31222
- https://github.com/snorkel-team/snorkel
- https://www.notion.so/CVE-2026-31222-35d1e139318881db8398e0732af8df6d
