# [M] Apache Log4j API: Improper encoding of non-finite floating-point values during MapMessage JSON serialization

## Summary
Severity: Medium
Advisory: GHSA-qv9r-c865-cp47
CVE: CVE-2026-49844
CWE: CWE-116
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:N/VI:N/VA:N/SC:N/SI:L/SA:N (CVSS_V4)
Published: 2026-07-11
Source: https://github.com/advisories/GHSA-qv9r-c865-cp47
Type: github-advisory

## Affected
- Maven: `org.apache.logging.log4j:log4j-api` — affected >=2.13.1 <2.25.5
- Maven: `org.apache.logging.log4j:log4j-api` — affected >=2.26.0 <2.26.1

## Details
Improper encoding of non-finite floating-point values during MapMessage JSON serialization in Apache Log4j API produces output that is not valid JSON. This issue affects Apache Log4j API versions 2.13.1 through 2.25.4 and version 2.26.0.

The fix for CVE-2026-34481 did not cover all code paths: when a MapMessage contains a non-finite IEEE 754 value (NaN, Infinity, or -Infinity), MapMessage.asJson() emits the corresponding bare token. RFC 8259 does not permit these tokens, so a conformant parser rejects the resulting document.

The defect is reachable only when both of the following conditions hold:

  *  The application uses the  message resolver https://logging.apache.org/log4j/2.x/manual/json-template-layout.html#event-template-resolver-message  of JsonTemplateLayout or any other layout that relies on MapMessage.asJson() or MapMessage.getFormattedMessage(new String[]{"JSON"}).
  *  The application logs a MapMessage that contains an attacker-controlled floating-point value.


An attacker who can supply a non-finite value can cause the affected layout to emit malformed JSON, which may corrupt the enclosing log record or disrupt downstream log ingestion and parsing.

Users are advised to upgrade to Apache Log4j API 2.25.5 or 2.26.1, both of which emit RFC 8259-compliant JSON for non-finite values.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-49844
- https://github.com/apache/logging-log4j2/pull/4163
- https://github.com/apache/logging-log4j2/commit/19edb23e162d6c728a8c2221a240037d389ed300
- https://github.com/apache/logging-log4j2/commit/feadf8eb0b4acb6ddfa4c0ab2bbc6d88b8e12d82
- https://github.com/apache/logging-log4j2
- https://github.com/apache/logging-log4j2/releases/tag/rel/2.25.5
- https://github.com/apache/logging-log4j2/releases/tag/rel/2.26.1
- https://logging.apache.org/cyclonedx/vdr.xml
- https://logging.apache.org/log4j/2.x/manual/json-template-layout.html#event-template-resolver-message
- https://logging.apache.org/security.html#CVE-2026-49844
