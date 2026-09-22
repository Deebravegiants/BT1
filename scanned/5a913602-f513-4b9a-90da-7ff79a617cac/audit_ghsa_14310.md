# [C] Expo SDK has an OAuth vulnerability

## Summary
Severity: Critical
Advisory: GHSA-wr5g-q49g-548w
CVE: CVE-2023-28131
CWE: CWE-522
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2023-04-24
Source: https://github.com/advisories/GHSA-wr5g-q49g-548w
Type: github-advisory

## Affected
- npm: `expo` — affected >=0 <48.0.0

## Details
A vulnerability in the expo.io framework allows an attacker to take over accounts and steal credentials on an application/website that configured the "Expo AuthSession Redirect Proxy" for social sign-in. This can be achieved once a victim clicks a malicious link. The link itself may be sent to the victim in various ways (including email, text message, an attacker-controlled website, etc).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-28131
- https://blog.expo.dev/security-advisory-for-developers-using-authsessions-useproxy-options-and-auth-expo-io-e470fe9346df
- https://github.com/expo/expo
- https://www.darkreading.com/endpoint/oauth-flaw-in-expo-platform-affects-hundreds-of-third-party-sites-apps
