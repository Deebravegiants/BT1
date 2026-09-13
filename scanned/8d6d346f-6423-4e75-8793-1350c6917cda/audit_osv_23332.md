# [M] CVE-2022-47934

## Summary
Severity: Medium
Advisory: CVE-2022-47934
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2022-12-24
Source: https://osv.dev/vulnerability/CVE-2022-47934
Type: osv

## Details
Brave Browser before 1.43.88 allowed a remote attacker to cause a denial of service in private and guest windows via a crafted HTML file that mentions an ipfs:// or ipns:// URL. This is caused by an incomplete fix for CVE-2022-47932 and CVE-2022-47934.

## References
- https://hackerone.com/reports/1646204
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/47xxx/CVE-2022-47934.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-47934
- https://github.com/brave/brave-browser/issues/24211
- https://github.com/brave/brave-browser/issues/25106
- https://github.com/brave/brave-core/commit/82d8e39043e691e0492519126437275511ee87e8
- https://github.com/brave/brave-core/pull/14313
