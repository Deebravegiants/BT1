# [M] OpenRefine Server-Side Request Forgery vulnerability

## Summary
Severity: Medium
Advisory: GHSA-q7mc-fc87-v7w7
CVE: CVE-2022-41401
CWE: CWE-918
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-08-04
Source: https://github.com/advisories/GHSA-q7mc-fc87-v7w7
Type: github-advisory

## Affected
- Maven: `org.openrefine:main` — affected >=0 <3.6.0

## Details
OpenRefine <= v3.5.2 contains a Server-Side Request Forgery (SSRF) vulnerability, which permits unauthorized users to exploit the system, potentially leading to unauthorized access to internal resources and sensitive file disclosure.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-41401
- https://github.com/OpenRefine/OpenRefine/commit/8cb2fec45dd90fda8ed9608c691f6bb8ed721cd2
- https://github.com/OpenRefine/OpenRefine
- https://github.com/OpenRefine/OpenRefine/blob/30d6edb7b6586623bda09456c797c35983fb80ff/main/tests/server/src/com/google/refine/importing/ImportingUtilitiesTests.java#L180
- https://github.com/OpenRefine/OpenRefine/blob/cb55cdfdf6f9ca916839778dc847cce803688998/main/src/com/google/refine/importing/ImportingUtilities.java#L103
- https://github.com/ixSly/CVE-2022-41401
