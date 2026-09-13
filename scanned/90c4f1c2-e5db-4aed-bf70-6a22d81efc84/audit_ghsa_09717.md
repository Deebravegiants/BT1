# [M] Apache Log4j 1 to Log4j 2 bridge: silent log event loss in Log4j1XmlLayout due to unescaped XML 1.0 forbidden characters

## Summary
Severity: Medium
Advisory: GHSA-h383-gmxw-35v2
CVE: CVE-2026-34479
CWE: CWE-116
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:N/SC:N/SI:L/SA:N (CVSS_V4)
Published: 2026-04-10
Source: https://github.com/advisories/GHSA-h383-gmxw-35v2
Type: github-advisory

## Affected
- Maven: `org.apache.logging.log4j:log4j-1.2-api` — affected >=2.7 <2.25.4
- Maven: `org.apache.logging.log4j:log4j-1.2-api` — affected >=3.0.0-beta1

## Details
The `Log4j1XmlLayout` from the Apache Log4j 1-to-Log4j 2 bridge fails to escape characters forbidden by the XML 1.0 standard, producing malformed XML output. Conforming XML parsers are required to reject documents containing such characters with a fatal error, which may cause downstream log processing systems to drop or fail to index affected records.

Two groups of users are affected:

* Those using `Log4j1XmlLayout` directly in a Log4j Core 2 configuration file.
* Those using the Log4j 1 configuration compatibility layer with `org.apache.log4j.xml.XMLLayout` specified as the layout class.

Users are advised to upgrade to Apache Log4j 1-to-Log4j 2 bridge version `2.25.4`, which corrects this issue.

> [!NOTE]
> The Apache Log4j 1-to-Log4j 2 bridge is deprecated and will not be present in Log4j 3. Users are encouraged to consult the
> [Log4j 1 to Log4j 2 migration guide](https://logging.apache.org/log4j/2.x/migrate-from-log4j1.html), and specifically the section on eliminating reliance on the bridge.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-34479
- https://github.com/apache/logging-log4j2/pull/4078
- https://github.com/apache/logging-log4j2
- https://lists.apache.org/thread/gd0hp6mj17rn3kj279vgy4p7kd4zz5on
- https://logging.apache.org/cyclonedx/vdr.xml
- https://logging.apache.org/log4j/2.x/migrate-from-log4j1.html
- https://logging.apache.org/security.html#CVE-2026-34479
- http://www.openwall.com/lists/oss-security/2026/04/10/8
