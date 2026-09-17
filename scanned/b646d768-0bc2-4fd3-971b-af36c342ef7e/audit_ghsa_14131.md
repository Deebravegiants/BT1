# [H] proxy denial of service vulnerability

## Summary
Severity: High
Advisory: GHSA-mj6p-3pc9-wf5m
CVE: CVE-2023-2968
CWE: CWE-232
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-05-30
Source: https://github.com/advisories/GHSA-mj6p-3pc9-wf5m
Type: github-advisory

## Affected
- npm: `proxy` — affected >=2.0.0 <2.1.1

## Details
A remote attacker can trigger a denial of service in the `socket.remoteAddress` variable, by sending a crafted HTTP request. Usage of the undefined variable raises a TypeError exception.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-2968
- https://github.com/TooTallNate/proxy-agents/pull/178
- https://github.com/TooTallNate/proxy-agents/commit/25e0c931390eb8f41c5ceaca72820de9198ece39
- https://github.com/TooTallNate/proxy-agents
- https://research.jfrog.com/vulnerabilities/undefined-variable-usage-in-proxy-leads-to-remote-denial-of-service-xray-520917
