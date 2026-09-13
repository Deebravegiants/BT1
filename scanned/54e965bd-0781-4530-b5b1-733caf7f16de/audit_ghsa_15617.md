# [H] speaker vulnerable to Denial of Service

## Summary
Severity: High
Advisory: GHSA-w5fc-gj3h-26rx
CVE: CVE-2024-21526
CWE: CWE-241, CWE-400
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2024-07-10
Source: https://github.com/advisories/GHSA-w5fc-gj3h-26rx
Type: github-advisory

## Affected
- npm: `speaker` — affected >=0

## Details
All versions of the package speaker are vulnerable to Denial of Service (DoS) when providing unexpected input types to the channels property of the Speaker object makes it possible to reach an assert macro. Exploiting this vulnerability can lead to a process crash.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-21526
- https://github.com/TooTallNate/node-speaker
- https://github.com/TooTallNate/node-speaker/blob/316afff5a393fce438cf7296011fcfc6e12aa9dc/src/binding.c#L48
- https://security.snyk.io/vuln/SNYK-JS-SPEAKER-6370676
