# [C] Expression Language Injection in Netflix Conductor

## Summary
Severity: Critical
Advisory: GHSA-wfj5-2mqr-7jvv
CVE: CVE-2020-9296
CWE: CWE-917
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-02-10
Source: https://github.com/advisories/GHSA-wfj5-2mqr-7jvv
Type: github-advisory

## Affected
- Maven: `com.netflix.conductor:conductor-core` — affected >=0 <2.25.4

## Details
Netflix Conductor uses Java Bean Validation (JSR 380) custom constraint validators. When building custom constraint violation error messages, different types of interpolation are supported, including Java EL expressions. If an attacker can inject arbitrary data in the error message template being passed to ConstraintValidatorContext.buildConstraintViolationWithTemplate() argument, they will be able to run arbitrary Java code.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-9296
- https://github.com/Netflix/security-bulletins/blob/master/advisories/nflx-2020-001.md
- https://github.com/Netflix/security-bulletins/blob/master/advisories/nflx-2020-002.md
