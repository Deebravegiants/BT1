# [M] Missing Cryptographic Step in OWASP Enterprise Security API for Java

## Summary
Severity: Medium
Advisory: GHSA-2g56-7jv7-wxxq
CVE: CVE-2013-5960
CWE: CWE-325
Ecosystem: Maven
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-2g56-7jv7-wxxq
Type: github-advisory

## Affected
- Maven: `org.owasp.esapi:esapi` — affected >=2.0.0.0 <2.1.0.1

## Details
The authenticated-encryption feature in the symmetric-encryption implementation in the OWASP Enterprise Security API (ESAPI) for Java 2.x before 2.1.0.1 does not properly resist tampering with serialized ciphertext, which makes it easier for remote attackers to bypass intended cryptographic protection mechanisms via an attack against the intended cipher mode in a non-default configuration, a different vulnerability than CVE-2013-5679.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2013-5960
- https://github.com/ESAPI/esapi-java-legacy/issues/359
- https://github.com/esapi/esapi-java-legacy/issues/306
- https://github.com/ESAPI/esapi-java-legacy/commit/b7cbc53f9cc967cf1a5a9463d8c6fef9ed6ef4f7
- https://github.com/ESAPI/esapi-java-legacy
- https://github.com/ESAPI/esapi-java-legacy/blob/master/documentation/esapi4java-core-2.1.0.1-release-notes.txt
- http://code.google.com/p/owasp-esapi-java/issues/detail?id=306
- http://lists.owasp.org/pipermail/esapi-dev/2013-August/002285.html
- http://owasp-esapi-java.googlecode.com/svn/trunk/documentation/ESAPI-security-bulletin1.pdf
