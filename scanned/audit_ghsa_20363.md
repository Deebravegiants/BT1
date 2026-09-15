# [H] Uncontrolled Resource Consumption in fast-string-search

## Summary
Severity: High
Advisory: GHSA-4263-q746-94mw
CVE: CVE-2022-22138
CWE: CWE-400, CWE-682
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-06-18
Source: https://github.com/advisories/GHSA-4263-q746-94mw
Type: github-advisory

## Affected
- npm: `fast-string-search` — affected >=0

## Details
All versions of package fast-string-search are vulnerable to Denial of Service (DoS) when computations are incorrect for non-string inputs. One can cause the V8 to attempt reading from non-permitted locations and cause a segmentation fault due to the violation.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-22138
- https://snyk.io/vuln/SNYK-JS-FASTSTRINGSEARCH-2392367
