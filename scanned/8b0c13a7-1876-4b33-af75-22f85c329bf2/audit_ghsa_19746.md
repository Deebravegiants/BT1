# [M] Apache Camel Message Header Injection through request parameters

## Summary
Severity: Medium
Advisory: GHSA-96v5-c2h5-56hm
CVE: CVE-2025-29891
CWE: CWE-164
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:N/I:L/A:L (CVSS_V3)
Published: 2025-03-12
Source: https://github.com/advisories/GHSA-96v5-c2h5-56hm
Type: github-advisory

## Affected
- Maven: `org.apache.camel:camel-support` — affected >=3.10.0 <3.22.4
- Maven: `org.apache.camel:camel-support` — affected >=4.9.0 <4.10.2
- Maven: `org.apache.camel:camel-support` — affected >=4.0.0-M1 <4.8.5

## Details
Bypass/Injection vulnerability in Apache Camel.

This issue affects Apache Camel: from 4.9.0 before 4.10.2, from 4.0.0 before 4.8.5, from 3.10.0 before 3.22.4.

Users are recommended to upgrade to version 4.10.2 for 4.10.x LTS, 4.8.5 for 4.8.x LTS and 3.22.4 for 3.x releases.

This vulnerability is present in Camel's default incoming header filter, that allows an attacker to include Camel specific headers that for some Camel components can alter the behaviours such as the camel-bean component, or the camel-exec component.

If you have Camel applications that are directly connected to the internet via HTTP, then an attacker could include parameters in the HTTP requests that are sent to the Camel application that get translated into headers. 

The headers could be both provided as request parameters for an HTTP methods invocation or as part of the payload of the HTTP methods invocation.

All the known Camel HTTP component such as camel-servlet, camel-jetty, camel-undertow, camel-platform-http, and camel-netty-http would be vulnerable out of the box.

This CVE is related to the CVE-2025-27636: while they have the same root cause and are fixed with the same fix, CVE-2025-27636 was assumed to only be exploitable if an attacker could add malicious HTTP headers, while we have now determined that it is also exploitable via HTTP parameters. Like in CVE-2025-27636, exploitation is only possible if the Camel route uses particular vulnerable components.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-29891
- https://github.com/apache/camel/commit/23a833eec6131a3cdce6e4b1b40b3ac2035b6adf
- https://github.com/apache/camel/commit/45a6b74f7f8af8fd58f197566938a9534392a624
- https://camel.apache.org/security/CVE-2025-27636.html
- https://camel.apache.org/security/CVE-2025-29891.html
- https://github.com/akamai/CVE-2025-27636-Apache-Camel-PoC
- https://github.com/apache/camel
- https://issues.apache.org/jira/browse/CAMEL-21828
