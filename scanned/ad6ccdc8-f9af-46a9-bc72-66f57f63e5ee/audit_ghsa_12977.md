# [H] FaucetSDN Ryu Denial of Service Vulnerability

## Summary
Severity: High
Advisory: GHSA-5x64-925v-h4gv
CVE: CVE-2020-35141
CWE: CWE-770, CWE-835
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-08-11
Source: https://github.com/advisories/GHSA-5x64-925v-h4gv
Type: github-advisory

## Affected
- PyPI: `ryu` — affected >=0

## Details
An issue was discovered in `OFPQueueGetConfigReply` in `parser.py` in FaucetSDN Ryu version 4.34, allows remote attackers to cause a denial of service (DoS) (infinite loop).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-35141
- https://github.com/faucetsdn/ryu/issues/118
- https://github.com/faucetsdn/ryu
