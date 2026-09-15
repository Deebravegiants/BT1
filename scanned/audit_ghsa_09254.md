# [H] FUXA Vulnerable to Pre-auth RCE via Path Manipulation & Configuration Injection

## Summary
Severity: High
Advisory: GHSA-p69w-mmfv-xrfj
CVE: CVE-2026-43945
CWE: CWE-284, CWE-288, CWE-863, CWE-94
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:P (CVSS_V4)
Published: 2026-05-26
Source: https://github.com/advisories/GHSA-p69w-mmfv-xrfj
Type: github-advisory

## Affected
- npm: `@frangoteam/fuxa` — affected >=1.2.11 <1.3.1

## Details
**Pre-auth** RCE in FUXA via Logic Bypass

Summary

A Critical vulnerability chain exists in FUXA (v.1.3.0-2706) that allows an unauthenticated remote attacker to achieve Full Remote Code Execution (RCE) as root. The exploit succeeds even when the platform is configured in its most secure state (Secure Mode Enabled and Node-RED Secure Auth Enabled).

Details
The vulnerability is a Path Confusion flaw in the authentication middleware. The server uses a substring match on the full URL (including query parameters) to exclude certain paths from authentication.

Involved Logic:

JavaScript:
```
const url = req.originalUrl || req.url || req.path;
if (url.includes('/socket.io')) return next();
By appending ?x=/socket.io to any administrative request, the middleware is "tricked" into treating the request as a public WebSocket handshake, bypassing the secureEnabled and nodeRedAuthMode checks entirely.
```

Proof of Concept

A specially crafted request containing manipulated query parameters could bypass authentication checks on protected /nodered/* endpoints.

In configurations where Node-RED exposed privileged or command-execution capable nodes, this could lead to remote code execution within the container context.

Impact
Access Level: Unauthenticated / Remote.

Privilege Level: Access to Node-RED administrative endpoints. 
Remote code execution may be possible depending on the Node-RED configuration and installed nodes.

CVSS 3.1 Score: High severity.

Description: An attacker can gain total control over the SCADA server, allowing them to intercept industrial data (MQTT/OPC-UA), manipulate PLC tags, or pivot into the internal OT network.

Root Cause & Remediation
The root cause is the reliance on req.originalUrl for security-critical routing decisions.

The Fix:
The developer must use req.path (which Express pre-parses to remove query strings) or a formal URL parser to ensure that the security check is performed only against the pathname.

```
JavaScript

// Secure approach
const pathname = req.path; 
if (pathname.startsWith('/socket.io/')) return next();
```

This issue affects only setups where Node-RED is enabled.

## References
- https://github.com/frangoteam/FUXA/security/advisories/GHSA-p69w-mmfv-xrfj
- https://github.com/frangoteam/FUXA
- https://github.com/frangoteam/FUXA/releases/tag/v1.3.1
