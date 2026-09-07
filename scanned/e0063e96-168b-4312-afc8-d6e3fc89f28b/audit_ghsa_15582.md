# [H] Gematik Referenzvalidator has an XXE vulnerability that can lead to a Server Side Request Forgery attack

## Summary
Severity: High
Advisory: GHSA-68j8-fp38-p48q
CVE: CVE-2024-46984
CWE: CWE-611
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2024-09-19
Source: https://github.com/advisories/GHSA-68j8-fp38-p48q
Type: github-advisory

## Affected
- Maven: `de.gematik.refv.commons:commons` — affected >=0 <2.5.1

## Details
### Impact
The profile location routine in the referencevalidator commons package is vulnerable to [XML External Entities](https://owasp.org/www-project-top-ten/2017/A4_2017-XML_External_Entities_(XXE)) attack due to insecure defaults of the used Woodstox WstxInputFactory. A malicious XML resource can lead to network requests issued by referencevalidator and thus to a [Server Side Request Forgery](https://owasp.org/www-community/attacks/Server_Side_Request_Forgery) attack.

The vulnerability impacts applications which use referencevalidator to process XML resources from untrusted sources. 

### Patches
The problem has been patched with the [2.5.1 version](https://github.com/gematik/app-referencevalidator/releases/tag/2.5.1) of the referencevalidator. Users are strongly recommended to update to this version or a more recent one. 

### Workarounds
A pre-processing or manual analysis of input XML resources on existence of DTD definitions or external entities can mitigate the problem.

### References
- [OWASP Top 10 XXE](https://owasp.org/www-project-top-ten/2017/A4_2017-XML_External_Entities_(XXE)#)
- [Server Side Request Forgery](https://owasp.org/www-community/attacks/Server_Side_Request_Forgery)
- [OWASP XML External Entity Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/XML_External_Entity_Prevention_Cheat_Sheet.html#transformerfactory)

## References
- https://github.com/gematik/app-referencevalidator/security/advisories/GHSA-68j8-fp38-p48q
- https://nvd.nist.gov/vuln/detail/CVE-2024-46984
- https://github.com/gematik/app-referencevalidator/commit/d6d27613fab7a8dd08534946f29e0c51f319cad6
- https://cheatsheetseries.owasp.org/cheatsheets/XML_External_Entity_Prevention_Cheat_Sheet.html#transformerfactory
- https://github.com/gematik/app-referencevalidator
- https://github.com/gematik/app-referencevalidator/releases/tag/2.5.1
- https://owasp.org/www-community/attacks/Server_Side_Request_Forgery
- https://owasp.org/www-project-top-ten/2017/A4_2017-XML_External_Entities_(XXE)
- https://owasp.org/www-project-top-ten/2017/A4_2017-XML_External_Entities_(XXE)#
