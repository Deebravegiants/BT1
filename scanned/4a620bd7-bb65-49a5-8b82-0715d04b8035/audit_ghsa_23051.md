# [H] Matrix Synapse DoS

## Summary
Severity: High
Advisory: GHSA-vmcc-4p4x-x7wg
CVE: CVE-2018-10657
CWE: CWE-20
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-vmcc-4p4x-x7wg
Type: github-advisory

## Affected
- PyPI: `matrix-synapse` — affected >=0 <0.28.1

## Details
Matrix Synapse before 0.28.1 is prone to a denial of service flaw where malicious events injected with depth = 2<sup>63</sup> - 1 render rooms unusable, related to `federation/federation_base.py` and `handlers/message.py`, as exploited in the wild in April 2018.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-10657
- https://github.com/matrix-org/synapse/commit/33f469ba19586bbafa0cf2c7d7c35463bdab87eb
- https://docs.google.com/document/d/1I3fi2S-XnpO45qrpCsowZv8P8dHcNZ4fsBsbOW7KABI/edit#heading=h.fj95ykuss7s1
- https://github.com/matrix-org/synapse
- https://matrix.org/blog/2018/05/01/security-update-synapse-0-28-1
