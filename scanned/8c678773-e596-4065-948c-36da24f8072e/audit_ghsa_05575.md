# [M] NocoDB has Unvalidated Redirect in Login Flow via continueAfterSignIn Parameter

## Summary
Severity: Medium
Advisory: GHSA-3hmw-8mw3-rmpj
CVE: CVE-2026-24768
CWE: CWE-601
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N/E:P (CVSS_V4)
Published: 2026-01-28
Source: https://github.com/advisories/GHSA-3hmw-8mw3-rmpj
Type: github-advisory

## Affected
- npm: `nocodb` — affected >=0 <0.301.0

## Details
### Summary

An **unvalidated redirect (open redirect)** vulnerability exists in NocoDB’s login flow due to missing validation of the `continueAfterSignIn` parameter.

During authentication, NocoDB processes a user-controlled redirect value and conditionally performs client-side navigation without enforcing any restrictions on the destination’s origin, domain or protocol. This allows attackers to redirect authenticated users to arbitrary external websites after login.

### Root Cause

The redirect logic relies on a permissive URL check that treats any absolute or protocol-relative URL as safe, and performs navigation without applying an allowlist or origin validation.

In the redirect plugin:

* The helper function `isFullUrl` uses the following regular expression:

  ```ts
  /^(https?:)?\/\//
  ```

  This pattern matches any HTTP(S) URL as well as protocol-relative URLs (e.g., `//evil.example`), without restricting allowed domains.

* When the `continueAfterSignIn` query parameter matches this pattern, the application performs an unconditional external navigation:

  ```ts
  navigateTo(route.value.query.continueAfterSignIn as string, {
    external: isFullUrl(...)
  })
  ```

### Attack Scenario

An attacker can exploit this issue through a phishing attack:

1. The attacker crafts a malicious login URL containing a controlled redirect target, for example:

   ```
   https://victim-nocodb.example/#/signin?continueAfterSignIn=https://evil-phishing.com/fake-login
   ```
2. The victim clicks the link and is presented with the legitimate NocoDB login page.
3. The victim authenticates using valid credentials.
4. After login, NocoDB automatically redirects the victim to the attacker-controlled external site.
5. The attacker’s site displays a fake error message and prompts the victim to re-enter credentials.
6. The victim unknowingly submits credentials to the attacker.

### Impact

This vulnerability enables **phishing attacks** by leveraging user trust in the legitimate NocoDB login flow. While it does not directly expose credentials or bypass authentication, it increases the likelihood of credential theft through social engineering.

The issue does not allow arbitrary code execution or privilege escalation, but it undermines authentication integrity.

### Credit

This issue was discovered by an AI agent developed by the GitHub Security Lab and reviewed by GHSL team members [@p- (Peter Stöckli)](https://github.com/p-) and [@m-y-mo (Man Yue Mo)](https://github.com/m-y-mo).

## References
- https://github.com/nocodb/nocodb/security/advisories/GHSA-3hmw-8mw3-rmpj
- https://nvd.nist.gov/vuln/detail/CVE-2026-24768
- https://github.com/nocodb/nocodb
