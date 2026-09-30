# [C] Server-Side Request Forgery in SLiMS

## Summary
Severity: Critical
Advisory: CVE-2023-3744
CVSS: 9.9 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2023-10-02
Source: https://osv.dev/vulnerability/CVE-2023-3744
Type: osv

## Details
Server-Side Request Forgery vulnerability in SLims version 9.6.0. This vulnerability could allow an authenticated attacker to send requests to internal services or upload the contents of relevant files via the "scrape_image.php" file in the imageURL parameter.

## References
- https://www.incibe.es/en/incibe-cert/notices/aviso/server-side-request-forgery-slims
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/3xxx/CVE-2023-3744.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-3744
