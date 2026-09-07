# [H] Cattown is Vulnerable to Uncontrolled Resource Consumption through Inefficient Regular Expression Complexity

## Summary
Severity: High
Advisory: GHSA-455v-w7r9-3vv9
CVE: CVE-2025-58451
CWE: CWE-1333, CWE-400
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-09-09
Source: https://github.com/advisories/GHSA-455v-w7r9-3vv9
Type: github-advisory

## Affected
- npm: `cattown` — affected >=0 <1.0.2

## Details
### Overview
A security review of the Cattown identified multiple weaknesses that could potentially impact its stability and security.

### Affected Versions
- All versions below 1.0.2

### Description of Vulnerabilities
1. CWE-1333: Inefficient Regular Expression Complexity
The package used regular expressions with inefficient, potentially exponential worst-case complexity. This can cause excessive CPU usage due to excessive backtracking on crafted inputs, potentially leading to denial of service.
2. CWE-400: Uncontrolled Resource Consumption (Resource Exhaustion)
The package was vulnerable to resource exhaustion, where processing malicious inputs could cause high CPU or memory usage, potentially leading to denial of service.

### Impact
- Trigger excessive CPU consumption leading to denial of service
- Cause resource exhaustion affecting service availability
- Bypass protection mechanisms causing unexpected or insecure behavior

### Resolution
These vulnerabilities have been fixed in version 1.0.2 of the Cattown. Users are strongly encouraged to upgrade to this version to mitigate the risks.

### Recommendations
- Upgrade to Cattown version 1.0.2 or later as soon as possible.
- Review and restrict input sources if untrusted inputs are processed.

### Acknowledgments
The issues were proactively identified through CodeQL static analysis.

## References
- https://github.com/IEatUranium238/Cattown/security/advisories/GHSA-455v-w7r9-3vv9
- https://nvd.nist.gov/vuln/detail/CVE-2025-58451
- https://github.com/IEatUranium238/Cattown/commit/70c2a28fb7dc520cfb7e401e0e141bff3dd26ead
- https://github.com/IEatUranium238/Cattown
- https://github.com/IEatUranium238/Cattown/releases/tag/security
- https://www.npmjs.com/package/cattown
