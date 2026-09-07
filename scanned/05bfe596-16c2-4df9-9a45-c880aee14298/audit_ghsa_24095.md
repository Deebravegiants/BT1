# [H] Signed to Unsigned Conversion Error in Facebook Hermes

## Summary
Severity: High
Advisory: GHSA-gmpm-xp43-f7g6
CVE: CVE-2020-1913
CWE: CWE-195, CWE-681
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-gmpm-xp43-f7g6
Type: github-advisory

## Affected
- npm: `hermes-engine` — affected >=0 <0.5.2

## Details
An Integer signedness error in the JavaScript Interpreter in Facebook Hermes prior to commit 2c7af7ec481ceffd0d14ce2d7c045e475fd71dc6 allows attackers to cause a denial of service attack or a potential RCE via crafted JavaScript. Note that this is only exploitable if the application using Hermes permits evaluation of untrusted JavaScript. Hence, most React Native applications are not affected.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-1913
- https://github.com/facebook/hermes/commit/2c7af7ec481ceffd0d14ce2d7c045e475fd71dc6
- https://www.facebook.com/security/advisories/cve-2020-1913
