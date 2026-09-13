# [C] safe-eval vulnerable to Sandbox Bypass due to improper input sanitization

## Summary
Severity: Critical
Advisory: GHSA-79xf-67r4-q2jj
CVE: CVE-2023-26122
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2023-04-11
Source: https://github.com/advisories/GHSA-79xf-67r4-q2jj
Type: github-advisory

## Affected
- npm: `safe-eval` — affected >=0

## Details
All versions of the package safe-eval are vulnerable to Sandbox Bypass due to improper input sanitization. The vulnerability is derived from prototype pollution exploitation. Exploiting this vulnerability might result in remote code execution (RCE).

**Vulnerable functions:**

__defineGetter__, stack(), toLocaleString(), propertyIsEnumerable.call(),  valueOf().

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-26122
- https://github.com/hacksparrow/safe-eval/issues/27
- https://github.com/hacksparrow/safe-eval/issues/31
- https://github.com/hacksparrow/safe-eval/issues/32
- https://github.com/hacksparrow/safe-eval/issues/33
- https://github.com/hacksparrow/safe-eval/issues/34
- https://github.com/hacksparrow/safe-eval/issues/35
- https://gist.github.com/seongil-wi/2db6cb884e10137a93132b7f74879cce
- https://github.com/hacksparrow/safe-eval
- https://security.snyk.io/vuln/SNYK-JS-SAFEEVAL-3373064
