# [M]  Apache Storm UI: Stored Cross-Site Scripting (XSS) via Unsanitized Topology Metadata

## Summary
Severity: Medium
Advisory: GHSA-f2hp-qw27-8wfq
CVE: CVE-2026-35565
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-04-13
Source: https://github.com/advisories/GHSA-f2hp-qw27-8wfq
Type: github-advisory

## Affected
- Maven: `org.apache.storm:storm-webapp` — affected >=0 <2.8.6

## Details
Stored Cross-Site Scripting (XSS) via Unsanitized Topology Metadata in Apache Storm UI


Versions Affected: before 2.8.6


Description: The Storm UI visualization component interpolates topology metadata including component IDs, stream names, and grouping values directly into HTML via innerHTML in parseNode() and parseEdge() without sanitization at any layer. An authenticated user with topology submission rights could craft a topology containing malicious HTML/JavaScript in component identifiers (e.g., a bolt ID containing an onerror event handler). This payload flows through Nimbus → Thrift → the Visualization API → vis.js tooltip rendering, resulting in stored cross-site scripting. 

In multi-tenant deployments where topology submission is available to less-trusted users but the UI is accessed by operators or administrators, this enables privilege escalation through script execution in an admin's browser session.


Mitigation: 2.x users should upgrade to 2.8.6. Users who cannot upgrade immediately should monkey-patch the parseNode() and parseEdge() functions in the visualization JavaScript file to HTML-escape all API-supplied values including nodeId, :capacity, :latency, :component, :stream, and :grouping before interpolation into tooltip HTML strings, and should additionally restrict topology submission to trusted users via Nimbus ACLs as a defense-in-depth measure. A guide on how to do this is available in the release notes of 2.8.6.

Credit: This issue was discovered while investigating another report by K.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-35565
- https://github.com/apache/storm
- https://storm.apache.org/2026/04/12/storm286-released.html
- http://www.openwall.com/lists/oss-security/2026/04/12/7
