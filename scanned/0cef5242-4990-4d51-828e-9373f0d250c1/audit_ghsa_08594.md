# [H] Snorkel BaseLabeler.load uses an unsafe pickle.load

## Summary
Severity: High
Advisory: GHSA-fq92-qc8f-482v
CVE: CVE-2026-31223
CWE: CWE-502
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-05-12
Source: https://github.com/advisories/GHSA-fq92-qc8f-482v
Type: github-advisory

## Affected
- PyPI: `snorkel` — affected >=0

## Details
The snorkel library thru v0.10.0 contains a critical insecure deserialization vulnerability (CWE-502) in the BaseLabeler.load() method of the BaseLabeler class. The method loads serialized labeler models using the unsafe pickle.load() function on user-supplied file paths without any validation or security controls. Python's pickle module is inherently dangerous for deserializing untrusted data, as it can execute arbitrary code during the deserialization process. A remote attacker can exploit this by providing a maliciously crafted pickle file, leading to arbitrary code execution on the victim's system when the file is loaded via the vulnerable method.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-31223
- https://github.com/snorkel-team/snorkel
- https://www.notion.so/CVE-2026-31223-35d1e1393188811ab1d0e4a8a2e67992
