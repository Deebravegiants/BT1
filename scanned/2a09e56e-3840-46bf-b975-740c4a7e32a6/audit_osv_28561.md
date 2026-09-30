# [H] CVE-2024-34487

## Summary
Severity: High
Advisory: CVE-2024-34487
Aliases: GHSA-m9vm-8mv9-v5v3, PYSEC-2026-1883
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-05
Source: https://osv.dev/vulnerability/CVE-2024-34487
Type: osv

## Details
OFPFlowStats in parser.py in Faucet SDN Ryu 4.34 allows attackers to cause a denial of service (infinite loop) via inst.length=0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/34xxx/CVE-2024-34487.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-34487
- https://github.com/faucetsdn/ryu/issues/192
