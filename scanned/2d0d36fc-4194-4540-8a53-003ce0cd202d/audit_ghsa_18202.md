# [M] express-xss-sanitizer has an unbounded recursion depth

## Summary
Severity: Medium
Advisory: GHSA-hvq2-wf92-j4f3
CVE: CVE-2025-59364
CWE: CWE-674
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-09-26
Source: https://github.com/advisories/GHSA-hvq2-wf92-j4f3
Type: github-advisory

## Affected
- npm: `express-xss-sanitizer` — affected >=0 <2.0.1

## Details
# Security Advisory: express-xss-sanitizer

## Overview
A vulnerability was discovered in express-xss-sanitizer that allowed unbounded recursion depth during sanitization of nested objects.

## Affected Versions
- All versions prior to 2.0.1

## Patched Versions
- 2.0.1 and later

## Description
The sanitize function in lib/sanitize.js performed recursive sanitization without depth limiting, making it vulnerable to stack overflow attacks via specially crafted deeply nested JSON objects.

## Impact
An attacker could cause denial-of-service by sending a request with deeply nested structures, potentially crashing the Node.js process.

## Solution
Upgrade to version 2.0.1 or later:

```bash
npm install express-xss-sanitizer@latest
```

## References
- https://github.com/AhmedAdelFahim/express-xss-sanitizer/security/advisories/GHSA-hvq2-wf92-j4f3
- https://nvd.nist.gov/vuln/detail/CVE-2025-59364
- https://github.com/AhmedAdelFahim/express-xss-sanitizer/pull/23
- https://github.com/AhmedAdelFahim/express-xss-sanitizer/commit/62d6542a2a57298da7a2e02de623454007e4f6d6
- https://dbugs.ptsecurity.com/vulnerability/PT-2025-37434
- https://gist.github.com/Spendroslav/177804eaef5acfb222a550de212a1b94
- https://github.com/AhmedAdelFahim/express-xss-sanitizer
- https://www.npmjs.com/package/express-xss-sanitizer
- https://www.tenable.com/cve/CVE-2025-59364
