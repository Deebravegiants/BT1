# [M] CSRF Vulnerability in jquery-ujs

## Summary
Severity: Medium
Advisory: GHSA-6qqj-rx4w-r3cj
CWE: CWE-352
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2020-08-31
Source: https://github.com/advisories/GHSA-6qqj-rx4w-r3cj
Type: github-advisory

## Affected
- npm: `jquery-ujs` — affected >=0 <1.0.4

## Details
Versions 1.0.3 and earlier of jquery-ujs are vulnerable to an information leakage attack that may enable attackers to launch CSRF attacks, as it allows attackers to send CSRF tokens to external domains.

When an attacker controls the href attribute of an anchor tag, or
the action attribute of a form tag triggering a POST action, the attacker can set the
href or action to " https://attacker.com". By prepending a space to the external domain, it causes jQuery to consider it a same origin request, resulting in the user's CSRF token being sent to the external domain.


## Recommendation

Upgrade jquery-ujs to version 1.0.4 or later.

## References
- https://hackerone.com/reports/49935
- https://groups.google.com/forum/#!msg/rubyonrails-security/XIZPbobuwaY/fqnzzpuOlA4J
- https://snyk.io/vuln/npm:jquery-ujs:20150624
- https://www.npmjs.com/advisories/15
