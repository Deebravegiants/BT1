# [H] CVE-2024-34483

## Summary
Severity: High
Advisory: CVE-2024-34483
Aliases: GHSA-7hmm-wg23-2w7m, PYSEC-2026-1879
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-05
Source: https://osv.dev/vulnerability/CVE-2024-34483
Type: osv

## Details
OFPGroupDescStats in parser.py in Faucet SDN Ryu 4.34 allows attackers to cause a denial of service (infinite loop) via OFPBucket.len=0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/34xxx/CVE-2024-34483.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-34483
- https://github.com/faucetsdn/ryu/issues/193
