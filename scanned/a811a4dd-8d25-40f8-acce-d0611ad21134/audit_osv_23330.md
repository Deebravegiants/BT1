# [M] CVE-2022-47932

## Summary
Severity: Medium
Advisory: CVE-2022-47932
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2022-12-24
Source: https://osv.dev/vulnerability/CVE-2022-47932
Type: osv

## Details
Brave Browser before 1.43.34 allowed a remote attacker to cause a denial of service via a crafted HTML file that mentions an ipfs:// or ipns:// URL. This vulnerability is caused by an incomplete fix for CVE-2022-47933.

## References
- https://hackerone.com/reports/1636430
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/47xxx/CVE-2022-47932.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-47932
- https://github.com/brave/brave-browser/issues/24093
- https://github.com/brave/brave-core/commit/e73309665508c17e48a67e302d3ab02a38d3ef50
- https://github.com/brave/brave-core/pull/14211
