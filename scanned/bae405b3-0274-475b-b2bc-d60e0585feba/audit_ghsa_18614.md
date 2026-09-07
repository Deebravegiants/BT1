# [M] marimo vulnerable to proxy abuse of /mpl/{port}/

## Summary
Severity: Medium
Advisory: GHSA-xjv7-6w92-42r7
CWE: CWE-441
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:L/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-10-01
Source: https://github.com/advisories/GHSA-xjv7-6w92-42r7
Type: github-advisory

## Affected
- PyPI: `marimo` — affected >=0.9.20 <0.16.4

## Details
### Summary
The  `/mpl/<port>/<route>` endpoint, which is accessible without authentication on default Marimo installations allows for external attackers to reach internal services and arbitrary ports. 

### Details
From our understanding, this route is used internally to provide access to interactive matplotlib visualizations.
[marimo/marimo/_server/main.py at main · marimo-team/marimo](https://github.com/marimo-team/marimo/blob/main/marimo/_server/main.py) 
This endpoint functions as an unauthenticated proxy, allowing an attacker to connect to any service running on the local machine via the specified `<port>` and `<route>`.

The existence of this proxy is visible in the application's code (marimo/_server/main.py), but there's no official documentation or warning about its behavior or potential risks.


### Impact
CWE-441: Proxying Without Authentication

This vulnerability, as it can be used to bypass firewalls and access internal services that are intended to be local-only. The level of impact depends entirely on what services are running and accessible on the local machine.

Full Local Access: An attacker can use this proxy to connect to local services that answer to web sockets, HTTP or ASGI protocol, effectively gaining a foothold on the machine. Depending on the service, this can lead to remote code execution, data exfiltration, or further network penetration.

Exposure of Sensitive Services: Our scans of public-facing Marimo servers have shown that many are exposing sensitive internal services, including:

Old CUPS Servers: Could allow an attacker to view print jobs or configuration or depending on old vulnerabilities, allow RCE.

phpMyAdmin: Provides a web interface to a MySQL database, potentially exposing sensitive data.

RPCMapper: Can be used for network reconnaissance and enumerating services.

While you’d hope people wouldn’t expose marimo instances to the internet, we found numerous public Marimo instances using tools like Shodan. Many of these servers, some even hosted on cloud platforms like AWS GovCloud, were found to be vulnerable. This means the vulnerability isn't limited to a few isolated cases but is a widespread issue affecting production environments.

===

Notes, this was discovered by [devgi](https://github.com/devgi). I ([acepace](https://github.com/acepace)) followed up and also created this report.

## References
- https://github.com/marimo-team/marimo/security/advisories/GHSA-xjv7-6w92-42r7
- https://github.com/marimo-team/marimo/commit/0312706d5e594acdb405209b2c8d87c98f46b22b
- https://github.com/marimo-team/marimo
- https://github.com/marimo-team/marimo/releases/tag/0.16.4
- https://marimo-team.notion.site/cve-proxy-without-authentication
