# [H] CVE-2022-47515

## Summary
Severity: High
Advisory: CVE-2022-47515
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-12-18
Source: https://osv.dev/vulnerability/CVE-2022-47515
Type: osv

## Details
An issue was discovered in drachtio-server before 0.8.20. It allows remote attackers to cause a denial of service (daemon crash) via a long message in a TCP request that leads to std::length_error.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/47xxx/CVE-2022-47515.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-47515
- https://github.com/drachtio/drachtio-server/issues/245
- https://github.com/drachtio/drachtio-server/commit/4cf9fe2c420b86c16442215d449d40be777c1911
