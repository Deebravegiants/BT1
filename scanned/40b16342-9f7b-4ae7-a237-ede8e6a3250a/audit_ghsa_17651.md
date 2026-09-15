# [M] @haxtheweb/haxcms-nodejs Iframe Phishing vulnerability

## Summary
Severity: Medium
Advisory: GHSA-v3ph-2q5q-cg88
CVE: CVE-2025-49139
CWE: CWE-1021
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2025-06-09
Source: https://github.com/advisories/GHSA-v3ph-2q5q-cg88
Type: github-advisory

## Affected
- npm: `@haxtheweb/haxcms-nodejs` — affected >=0 <11.0.0

## Details
### Summary

In the HAX site editor, users can create a website block to load another site in an iframe. The application allows users to supply a target URL in the website block. When the HAX site is visited, the client's browser will query the supplied URL.

### Affected Resources

- [Operations.php:868](https://github.com/haxtheweb/haxcms-php/blob/master/system/backend/php/lib/Operations.php#L868)
- `https://<site>/<user>/system/api/saveNode`

### PoC

1. Set the URL in an iframe pointing to an attacker-controlled server running Responder

![image](https://github.com/user-attachments/assets/baac23ec-7b1e-49cf-864d-c3550b2c71bf)

2. Once another user visits the site, they are prompted to sign in.

![image](https://github.com/user-attachments/assets/a3a0b75d-e12f-49cf-8669-9686353a92e2)

3. If a user inputs credentials, the username and password hash are outputted in Responder.

![image](https://github.com/user-attachments/assets/428542d3-8cf5-4bfa-b759-e630c3ee6ac3)

### Impact

An authenticated attacker can create a HAX site with a website block pointing at an attacker-controlled server running Responder or a similar tool. The attacker can then conduct a phishing attack by convincing another user to visit their malicious HAX site to harvest credentials.

## References
- https://github.com/haxtheweb/issues/security/advisories/GHSA-v3ph-2q5q-cg88
- https://nvd.nist.gov/vuln/detail/CVE-2025-49139
- https://github.com/haxtheweb/haxcms-nodejs/commit/5368eb9b278ca47cd9a83b8d3e6216375615b8f5
- https://github.com/haxtheweb/issues
