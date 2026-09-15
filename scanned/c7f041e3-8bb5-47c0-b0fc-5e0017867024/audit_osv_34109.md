# [H] Vision UI's security-kit Contains Cryptographic Weakness

## Summary
Severity: High
Advisory: CVE-2025-54883
Aliases: GHSA-c9xg-x7h3-mq2q
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:N/SC:L/SI:L/SA:N)
Published: 2025-08-05
Source: https://osv.dev/vulnerability/CVE-2025-54883
Type: osv

## Details
Vision UI is a collection of enterprise-grade, dependency-free modules for modern web projects. In versions 1.4.0 and below, the getSecureRandomInt function in security-kit versions prior to 3.5.0 (packaged in Vision-ui <= 1.4.0) contains a critical cryptographic weakness. Due to a silent 32-bit integer overflow in its internal masking logic, the function fails to produce a uniform distribution of random numbers when the requested range between min and max is larger than 2³². The root cause is the use of a 32-bit bitwise left-shift operation (<<) to generate a bitmask for the rejection sampling algorithm. This causes the mask to be incorrect for any range requiring 32 or more bits of entropy. This issue is fixed in version 1.5.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/54xxx/CVE-2025-54883.json
- https://github.com/DavidOsipov/Vision-ui/security/advisories/GHSA-c9xg-x7h3-mq2q
- https://nvd.nist.gov/vuln/detail/CVE-2025-54883
- https://github.com/DavidOsipov/Vision-ui/commit/347355859f05e98047efbd96fc0e61b9191324f1
