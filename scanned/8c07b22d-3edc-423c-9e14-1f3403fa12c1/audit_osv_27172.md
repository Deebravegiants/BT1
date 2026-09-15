# [M] Denial of Service in automatic1111/stable-diffusion-webui

## Summary
Severity: Medium
Advisory: CVE-2024-12074
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-03-20
Source: https://osv.dev/vulnerability/CVE-2024-12074
Type: osv

## Details
A Denial of Service (DoS) vulnerability was discovered in the file upload feature of automatic1111/stable-diffusion-webui version 1.10.0. The vulnerability is due to improper handling of form-data with a large filename in the file upload request. By sending a payload with an excessively large filename, the server becomes overwhelmed and unresponsive, leading to unavailability for legitimate users. This issue can be exploited without authentication, making it highly scalable and increasing the risk of exploitation.

## References
- https://huntr.com/bounties/6b44bfc2-31a7-4fe9-86fb-072c90a23642
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/12xxx/CVE-2024-12074.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-12074
