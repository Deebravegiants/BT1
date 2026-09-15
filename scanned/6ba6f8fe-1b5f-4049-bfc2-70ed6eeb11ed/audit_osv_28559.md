# [M] CVE-2024-34484

## Summary
Severity: Medium
Advisory: CVE-2024-34484
Aliases: GHSA-c7w6-33j3-j3mx, PYSEC-2026-1880
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N)
Published: 2024-05-05
Source: https://osv.dev/vulnerability/CVE-2024-34484
Type: osv

## Details
OFPBucket in parser.py in Faucet SDN Ryu 4.34 allows attackers to cause a denial of service (infinite loop) via action.len=0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/34xxx/CVE-2024-34484.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-34484
- https://github.com/faucetsdn/ryu/issues/194
