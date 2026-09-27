# [C] OpenAM: Unauthenticated Remote Code Execution via Class.forName in AuthXMLUtils.createCustomCallback

## Summary
Severity: Critical
Advisory: GHSA-wg5r-wc3x-39vc
CVE: CVE-2026-62379
CWE: CWE-470, CWE-94
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-07-24
Source: https://github.com/advisories/GHSA-wg5r-wc3x-39vc
Type: github-advisory

## Affected
- Maven: `org.openidentityplatform.openam:openam-core` — affected >=0 <16.1.2

## Details
## Summary
A pre-authentication remote code execution vulnerability affects OpenAM. The
remote authentication endpoint (`/authservice`, PLL) accepts an XML element
that names an arbitrary Java class, which the server then loads and
instantiates without validation. On a default configuration this is reachable
**without authentication** and allows an attacker to run code on the server.

## Impact
Unauthenticated remote code execution / full server compromise on any OpenAM
instance with default settings.

## Affected
All releases up to and including 16.1.1 (the defect predates the Open Identity
Platform fork).

## Remediation
Upgrade to `16.1.2`. The fix resolves the class named in a `<CustomCallback>`
element without running its static initialisers and rejects it unless it
implements `DSAMECallbackInterface`, and it constrains deserialisation of the
serialised `Subject` value to a class allowlist.

## Interim mitigation
If you cannot upgrade immediately:

- **Restrict or block external network access to `/authservice`.** This is the
  only reliable mitigation.
- Optionally, **block PLL requests carrying a `<CustomCallback className="...">`
  element** at the reverse proxy or WAF. That element is only produced for custom
  `DSAMECallbackInterface` callbacks, so most deployments never send it — confirm
  against your own traffic before enforcing.
- **Enabling `sunRemoteAuthSecurityEnabled` does *not* mitigate this issue.** The
  remote-auth security token is checked in `AuthXMLHandler.processAuthXMLRequest`,
  which runs only after `AuthXMLRequest.parseXML` has already parsed the request
  and instantiated the class named in the `<CustomCallback className="...">`
  element. Do not rely on it as a substitute for upgrading or for network
  restriction.

## Credit
Vulnerability discovered by Zhixi "Jace" Sun of ASM/VI at TikTok.
Correction of the interim mitigation guidance contributed by @BarakSrour.

## References
- https://github.com/OpenIdentityPlatform/OpenAM/security/advisories/GHSA-wg5r-wc3x-39vc
- https://github.com/OpenIdentityPlatform/OpenAM/commit/edcf968cad91a78b932dba4ad559ef94cbf35f5a
- https://github.com/OpenIdentityPlatform/OpenAM
- https://github.com/OpenIdentityPlatform/OpenAM/releases/tag/16.1.2
