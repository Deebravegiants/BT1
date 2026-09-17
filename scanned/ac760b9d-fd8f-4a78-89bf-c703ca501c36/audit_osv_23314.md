# [H] CVE-2022-47517

## Summary
Severity: High
Advisory: CVE-2022-47517
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-12-18
Source: https://osv.dev/vulnerability/CVE-2022-47517
Type: osv

## Details
An issue was discovered in the libsofia-sip fork in drachtio-server before 0.8.19. It allows remote attackers to cause a denial of service (daemon crash) via a crafted UDP message that causes a url_canonize2 heap-based buffer over-read because of an off-by-one error.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/47xxx/CVE-2022-47517.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-47517
- https://github.com/drachtio/drachtio-server/issues/243
- https://github.com/davehorton/sofia-sip/commit/22c1bd191f0acbf11f0c0fbea1845d9bf9dcd47e
- https://github.com/davehorton/sofia-sip/commit/bfc79d85c8f3a4798a3305fb98f5a11c11d0d29f
