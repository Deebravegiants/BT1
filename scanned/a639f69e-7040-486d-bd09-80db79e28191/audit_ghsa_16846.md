# [C] python-jose algorithm confusion with OpenSSH ECDSA keys

## Summary
Severity: Critical
Advisory: GHSA-6c5p-j8vq-pqhj
CVE: CVE-2024-33663
CWE: CWE-327
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2024-04-26
Source: https://github.com/advisories/GHSA-6c5p-j8vq-pqhj
Type: github-advisory

## Affected
- PyPI: `python-jose` — affected >=0 <3.4.0

## Details
python-jose through 3.3.0 has algorithm confusion with OpenSSH ECDSA keys and other key formats. This is similar to CVE-2022-29217.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-33663
- https://github.com/mpdavis/python-jose/issues/346
- https://github.com/mpdavis/python-jose
- https://github.com/pypa/advisory-database/tree/main/vulns/python-jose/PYSEC-2024-232.yaml
- https://www.vicarius.io/vsociety/posts/algorithm-confusion-in-python-jose-cve-2024-33663
