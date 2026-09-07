# [M] Allegro AI ClearML Stores Credentials in Plaintext in MongoDB Instance

## Summary
Severity: Medium
Advisory: GHSA-gvqv-h7hh-6fcc
CVE: CVE-2024-24595
CWE: CWE-312, CWE-522
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2024-02-06
Source: https://github.com/advisories/GHSA-gvqv-h7hh-6fcc
Type: github-advisory

## Affected
- PyPI: `clearml` — affected >=0

## Details
Allegro AI’s open-source version of ClearML stores passwords in plaintext within the MongoDB instance, resulting in a compromised server leaking all user emails and passwords.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-24595
- https://github.com/allegroai/clearml
- https://hiddenlayer.com/research/not-so-clear-how-mlops-solutions-can-muddy-the-waters-of-your-supply-chain
