# [H] Ryu Infinite Loop vulnerability

## Summary
Severity: High
Advisory: GHSA-ffp9-pfq9-g2ww
CVE: CVE-2024-34488
CWE: CWE-835
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2024-05-05
Source: https://github.com/advisories/GHSA-ffp9-pfq9-g2ww
Type: github-advisory

## Affected
- PyPI: `ryu` — affected >=0

## Details
`OFPMultipartReply` in parser.py in Faucet SDN Ryu 4.34 allows attackers to cause a denial of service (infinite loop) via `b.length=0`.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-34488
- https://github.com/faucetsdn/ryu/issues/191
- https://github.com/faucetsdn/ryu
