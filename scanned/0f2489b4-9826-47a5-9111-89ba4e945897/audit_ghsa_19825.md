# [H] H2O Vulnerable to Denial of Service (DoS) via `/3/ImportFiles` Endpoint

## Summary
Severity: High
Advisory: GHSA-p2vc-m5fv-9w9m
CVE: CVE-2024-7768
CWE: CWE-400, CWE-770
Ecosystem: Maven, PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2025-03-20
Source: https://github.com/advisories/GHSA-p2vc-m5fv-9w9m
Type: github-advisory

## Affected
- PyPI: `h2o` — affected >=0
- Maven: `ai.h2o:h2o-core` — affected >=0

## Details
A vulnerability in the `/3/ImportFiles` endpoint of h2oai/h2o-3 version 3.46.1 allows an attacker to cause a denial of service. The endpoint takes a single GET parameter, `path`, which can be recursively set to reference itself. This leads the server to repeatedly call its own endpoint, eventually filling up the request queue and leaving the server unable to handle other requests.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-7768
- https://github.com/h2oai/h2o-3
- https://github.com/h2oai/h2o-3/blob/7d418fa19d3ab434f742818e37f891bef9102c97/h2o-core/src/main/java/water/api/ImportFilesHandler.java#L19
- https://huntr.com/bounties/3fe640df-bef4-4072-8890-0d12bc2818f6
