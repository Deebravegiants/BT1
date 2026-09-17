# [H] Unauthenticated DoS via Multipart Boundary in automatic1111/stable-diffusion-webui

## Summary
Severity: High
Advisory: CVE-2024-10935
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-03-20
Source: https://osv.dev/vulnerability/CVE-2024-10935
Type: osv

## Details
automatic1111/stable-diffusion-webui version 1.10.0 contains a vulnerability where the server fails to handle excessive characters appended to the end of multipart boundaries. This flaw can be exploited by sending malformed multipart requests with arbitrary characters at the end of the boundary, leading to excessive resource consumption and a complete denial of service (DoS) for all users. The vulnerability is unauthenticated, meaning no user login or interaction is required for an attacker to exploit this issue.

## References
- https://huntr.com/bounties/e6fdc6ed-f38d-4798-b60a-0e47893a81a6
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/10xxx/CVE-2024-10935.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-10935
