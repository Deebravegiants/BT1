# [M] CVE-2022-43776

## Summary
Severity: Medium
Advisory: CVE-2022-43776
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2022-10-26
Source: https://osv.dev/vulnerability/CVE-2022-43776
Type: osv

## Details
The url parameter of the /api/geojson endpoint in Metabase versions <44.5 can be used to perform Server Side Request Forgery attacks. Previously implemented blacklists could be circumvented by leveraging 301 and 302 redirects.

## References
- https://www.tenable.com/security/research/tra-2022-34
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/43xxx/CVE-2022-43776.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-43776
