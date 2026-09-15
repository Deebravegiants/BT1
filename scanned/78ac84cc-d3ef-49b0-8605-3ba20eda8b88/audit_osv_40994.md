# [H] Elysia: Inefficient Algorithmic Complexity and Interpretation Conflict

## Summary
Severity: High
Advisory: CVE-2026-56669
Aliases: GHSA-9643-4qgh-g8mx
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-07-08
Source: https://osv.dev/vulnerability/CVE-2026-56669
Type: osv

## Details
Elysia is a Typescript framework for request validation, type inference, OpenAPI documentation, and client-server communication. Prior to 1.4.29, Elysia uses getAll in form data normalization for multipart/form-data endpoints, causing the amount of work to grow quadratically with the number of unique key-value pairs and allowing CPU exhaustion. This issue is fixed in version 1.4.29.

## References
- https://gist.github.com/jviide/ea040eabe7bac058326174e2cd42dfd9
- https://github.com/elysiajs/elysia/releases/tag/1.4.29
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/56xxx/CVE-2026-56669.json
- https://github.com/elysiajs/elysia/security/advisories/GHSA-9643-4qgh-g8mx
- https://nvd.nist.gov/vuln/detail/CVE-2026-56669
- https://github.com/elysiajs/elysia/commit/8358ff9efbcedf9534995f5977f26b9ceab59329
