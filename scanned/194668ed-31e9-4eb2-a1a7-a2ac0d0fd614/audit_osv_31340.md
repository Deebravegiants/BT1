# [H] Unauthenticated Denial of Service in transformeroptimus/superagi

## Summary
Severity: High
Advisory: CVE-2024-9437
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-03-20
Source: https://osv.dev/vulnerability/CVE-2024-9437
Type: osv

## Details
SuperAGI version v0.0.14 is vulnerable to an unauthenticated Denial of Service (DoS) attack. The vulnerability exists in the resource upload request, where appending characters, such as dashes (-), to the end of a multipart boundary in an HTTP request causes the server to continuously process each character. This leads to excessive resource consumption and renders the service unavailable. The issue is unauthenticated and does not require any user interaction, impacting all users of the service.

## References
- https://huntr.com/bounties/27404e9c-eb3d-4626-a9d9-8dc1b3295ce0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/9xxx/CVE-2024-9437.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-9437
