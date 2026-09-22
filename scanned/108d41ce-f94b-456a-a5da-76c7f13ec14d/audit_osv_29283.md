# [H] CVE-2024-41262

## Summary
Severity: High
Advisory: CVE-2024-41262
CVSS: 7.4 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2024-07-31
Source: https://osv.dev/vulnerability/CVE-2024-41262
Type: osv

## Details
mmudb v1.9.3 was discovered to use the HTTP protocol in the ShowMetricsRaw and ShowMetricsAsText functions, possibly allowing attackers to intercept communications via a man-in-the-middle attack.

## References
- https://gist.github.com/nyxfqq/c796ef4a0f3d93736c42022e085f78d7
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/41xxx/CVE-2024-41262.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-41262
