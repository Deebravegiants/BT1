# [H] CVE-2024-34489

## Summary
Severity: High
Advisory: CVE-2024-34489
Aliases: GHSA-59p2-v62x-gxj8, PYSEC-2026-1877
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-05
Source: https://osv.dev/vulnerability/CVE-2024-34489
Type: osv

## Details
OFPHello in parser.py in Faucet SDN Ryu 4.34 allows attackers to cause a denial of service (infinite loop) via length=0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/34xxx/CVE-2024-34489.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-34489
- https://github.com/faucetsdn/ryu/issues/195
