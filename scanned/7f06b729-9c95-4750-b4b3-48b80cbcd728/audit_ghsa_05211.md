# [M] malla: Stored XSS via Meshtastic node names in multiple frontend pages

## Summary
Severity: Medium
Advisory: GHSA-ch57-39q2-4crm
CVE: CVE-2026-43980
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2026-06-03
Source: https://github.com/advisories/GHSA-ch57-39q2-4crm
Type: github-advisory

## Affected
- PyPI: `malla` — affected >=0

## Details
Node names (long_name, short_name) received via MQTT are stored in SQLite without sanitization and rendered into the DOM without escaping.
Any participant on a public Meshtastic MQTT broker can set a malicious node name that executes JavaScript in the browser of every Malla dashboard visitor.

Affected files:

 - src/malla/templates/traceroute_graph.html (line ~832)
 - src/malla/templates/map.html (lines ~945, 1078)
 - src/malla/templates/packet_detail.html (lines ~1402, 1452)
 - src/malla/static/js/relay_node_analysis.js (line ~124)

Steps to reproduce

 1. Publish a Meshtastic NODEINFO_APP packet to any public MQTT broker with long_name set to a HTML entity i.e `<img src=x onerror=alert(1)>`
 2. Wait for malla-capture to store it
 3. Open the dashboard

Impact

Allows unauthenticated remote attackers to execute arbitrary JavaScript in the browser, such as: 

 - Phishing overlays
 - Force redirect to malicious websites
 - Injection of arbitrary third-party scripts (no CSP restrictions)
 - Browser resource abuse 
 - Persistent dashboard denial of service

## References
- https://github.com/zenitraM/malla/security/advisories/GHSA-ch57-39q2-4crm
- https://github.com/zenitraM/malla/commit/4086e2b5f61615a813b70b25bc76095083552135
- https://github.com/zenitraM/malla
