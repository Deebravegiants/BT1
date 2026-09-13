# [H] CVE-2024-22873

## Summary
Severity: High
Advisory: CVE-2024-22873
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:N)
Published: 2024-02-26
Source: https://osv.dev/vulnerability/CVE-2024-22873
Type: osv

## Details
Tencent Blueking CMDB v3.2.x to v3.9.x was discovered to contain a Server-Side Request Forgery (SSRF) via the event subscription function (/service/subscription.go). This vulnerability allows attackers to access internal requests via a crafted POST request.

## References
- https://gist.github.com/exp1orer/0f190c6a64b668a9b1c4c47789affa09
- https://sphenoid-enquiry-9be.notion.site/BK-CMDB-SSRF-ba21e94f4976460188fa52d26c15a6ae?pvs=4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/22xxx/CVE-2024-22873.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-22873
