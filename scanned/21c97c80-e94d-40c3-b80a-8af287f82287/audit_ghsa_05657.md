# [H] AssertJ has XML External Entity (XXE) vulnerability when parsing untrusted XML via isXmlEqualTo assertion

## Summary
Severity: High
Advisory: GHSA-rqfh-9r24-8c9r
CVE: CVE-2026-24400
CWE: CWE-611
Ecosystem: Maven
CVSS: CVSS:4.0/AV:L/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:L/SC:H/SI:N/SA:N (CVSS_V4)
Published: 2026-01-26
Source: https://github.com/advisories/GHSA-rqfh-9r24-8c9r
Type: github-advisory

## Affected
- Maven: `org.assertj:assertj-core` — affected >=1.4.0 <3.27.7

## Details
An XML External Entity (XXE) vulnerability exists in `org.assertj.core.util.xml.XmlStringPrettyFormatter`: the `toXmlDocument(String)` method initializes `DocumentBuilderFactory` with default settings, without disabling DTDs or external entities. This formatter is used by the `isXmlEqualTo(CharSequence)` assertion for `CharSequence` values.

An application is vulnerable only when it uses untrusted XML input with one of the following methods:

- `isXmlEqualTo(CharSequence)` from `org.assertj.core.api.AbstractCharSequenceAssert`
- `xmlPrettyFormat(String)` from `org.assertj.core.util.xml.XmlStringPrettyFormatter`

### Impact

If untrusted XML input is processed by the methods mentioned above (e.g., in test environments handling external fixture files), an attacker could:

- **Read arbitrary local files** via `file://` URIs (e.g., `/etc/passwd`, application configuration files)
- **Perform Server-Side Request Forgery (SSRF)** via HTTP/HTTPS URIs
- **Cause Denial of Service** via "Billion Laughs" entity expansion attacks

### Mitigation

`isXmlEqualTo(CharSequence)` has been deprecated in favor of [XMLUnit](https://www.xmlunit.org/) in version 3.18.0 and will be removed in version 4.0. Users of affected versions should, in order of preference:

1. Replace `isXmlEqualTo(CharSequence)` with XMLUnit, or
2. Upgrade to version 3.27.7, or
3. Avoid using `isXmlEqualTo(CharSequence)` or `XmlStringPrettyFormatter` with untrusted input.

`XmlStringPrettyFormatter` has historically been considered a utility for `isXmlEqualTo(CharSequence)` rather than a feature for AssertJ users, so it is deprecated in version 3.27.7 and removed in version 4.0, with no replacement.

### References

- [CWE-611: Improper Restriction of XML External Entity Reference](https://cwe.mitre.org/data/definitions/611.html)
- [OWASP XXE Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/XML_External_Entity_Prevention_Cheat_Sheet.html)

## References
- https://github.com/assertj/assertj/security/advisories/GHSA-rqfh-9r24-8c9r
- https://nvd.nist.gov/vuln/detail/CVE-2026-24400
- https://github.com/assertj/assertj/commit/85ca7eb6609bb179c043b85ae7d290523b1ba79a
- https://cheatsheetseries.owasp.org/cheatsheets/XML_External_Entity_Prevention_Cheat_Sheet.html
- https://github.com/assertj/assertj
- https://github.com/assertj/assertj/releases/tag/assertj-build-3.27.7
