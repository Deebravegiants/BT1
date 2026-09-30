# [H] SSRF Vulnerability in stangirard/quivr

## Summary
Severity: High
Advisory: CVE-2024-4851
CVSS: 7.7 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N)
Published: 2024-06-06
Source: https://osv.dev/vulnerability/CVE-2024-4851
Type: osv

## Details
A Server-Side Request Forgery (SSRF) vulnerability exists in the stangirard/quivr application, version 0.0.204, which allows attackers to access internal networks. The vulnerability is present in the crawl endpoint where the 'url' parameter can be manipulated to send HTTP requests to arbitrary URLs, thereby facilitating SSRF attacks. The affected code is located in the backend/routes/crawl_routes.py file, specifically within the crawl_endpoint function. This issue could allow attackers to interact with internal services that are accessible from the server hosting the application.

## References
- https://huntr.com/bounties/b6011986-954a-47da-a60c-fc7aebc8005d
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/4xxx/CVE-2024-4851.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-4851
