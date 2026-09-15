# [C] Salesforce Uni2TS has a Code Injection vulnerability

## Summary
Severity: Critical
Advisory: GHSA-7x99-8x99-xc54
CVE: CVE-2026-22584
CWE: CWE-94
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-01-10
Source: https://github.com/advisories/GHSA-7x99-8x99-xc54
Type: github-advisory

## Affected
- PyPI: `uni2ts` — affected >=0 <2.0.0

## Details
Improper Control of Generation of Code ('Code Injection') vulnerability in Salesforce Uni2TS on MacOS, Windows, Linux allows Leverage Executable Code in Non-Executable Files.This issue affects Uni2TS: through 1.2.0.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-22584
- https://github.com/SalesforceAIResearch/uni2ts/pull/218
- https://github.com/SalesforceAIResearch/uni2ts/commit/7f2d51dd729de018f0f22504f39a8475c6fed1c4
- https://github.com/SalesforceAIResearch/uni2ts
- https://github.com/SalesforceAIResearch/uni2ts/releases/tag/2.0.0
- https://help.salesforce.com/s/articleView?id=005239354&type=1
