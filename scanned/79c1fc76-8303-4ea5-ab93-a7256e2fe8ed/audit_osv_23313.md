# [H] CVE-2022-47516

## Summary
Severity: High
Advisory: CVE-2022-47516
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-12-18
Source: https://osv.dev/vulnerability/CVE-2022-47516
Type: osv

## Details
An issue was discovered in the libsofia-sip fork in drachtio-server before 0.8.20. It allows remote attackers to cause a denial of service (daemon crash) via a crafted UDP message that leads to a failure of the libsofia-sip-ua/tport/tport.c self assertion.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/47xxx/CVE-2022-47516.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-47516
- https://www.debian.org/security/2023/dsa-5410
- https://github.com/drachtio/drachtio-server/issues/244
- https://github.com/davehorton/sofia-sip/commit/13b2a135287caa2d67ac6cd5155626821e25b377
- https://lists.debian.org/debian-lts-announce/2023/02/msg00028.html
