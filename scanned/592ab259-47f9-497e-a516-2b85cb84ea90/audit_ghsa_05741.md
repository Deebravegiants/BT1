# [M] Mailpit Proxy Endpoint has Server-Side Request Forgery (SSRF) vulnerability

## Summary
Severity: Medium
Advisory: GHSA-8v65-47jx-7mfr
CVE: CVE-2026-21859
CWE: CWE-918
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:L/I:N/A:N (CVSS_V3)
Published: 2026-01-06
Source: https://github.com/advisories/GHSA-8v65-47jx-7mfr
Type: github-advisory

## Affected
- Go: `github.com/axllent/mailpit` — affected >=0 <1.28.1

## Details
## Summary

A Server-Side Request Forgery (SSRF) vulnerability exists in Mailpit's `/proxy` endpoint that allows attackers to make requests to internal network resources.


## Description

The `/proxy` endpoint allows requests to internal network resources. While it validates `http://` and `https://` schemes, it does not block internal IP addresses, allowing attackers to access internal services and APIs.

## Proof of Concept

### Basic SSRF Request
```
GET /proxy?url=http://127.0.0.1:8025/api/v1/info
```

This returns internal API data including database path and runtime statistics.
 
## Impact Assessment

### 1. Internal Network Scanning
Attacker can probe and discover internal services on the network.

### 2. Information Disclosure
Access to internal API data, database paths, and runtime statistics.

### 3. Email Content Access
Ability to read all captured emails via internal API endpoints.

### 4. Cloud Metadata Access
If deployed in cloud environments (AWS/GCP/Azure), potential access to instance metadata services (e.g., `http://169.254.169.254/`).

## Attack Scenarios

### Scenario 1: Development Environment Exposure
If Mailpit is accidentally exposed to the internet, attackers can leverage SSRF to access internal development resources and services.

### Scenario 2: Container Escape Information
In containerized deployments, SSRF can reveal container metadata and internal service configurations.

### Scenario 3: Lateral Movement
In corporate networks, SSRF can be used to discover and interact with internal services, facilitating lateral movement.

## Mitigating Factors
This vulnerability is limited to HTTP GET requests with minimal headers. Additionally, Mailpit's web UI & API should be protected by basic authentication when exposed to the internet, which prevents access to the proxy endpoint. 

## References

- [MDN Web Security - SSRF Attacks](https://developer.mozilla.org/en-US/docs/Web/Security/Attacks/SSRF)
- [CWE-918: Server-Side Request Forgery](https://cwe.mitre.org/data/definitions/918.html)
- [OWASP SSRF Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html)

## References
- https://github.com/axllent/mailpit/security/advisories/GHSA-8v65-47jx-7mfr
- https://nvd.nist.gov/vuln/detail/CVE-2026-21859
- https://github.com/axllent/mailpit/commit/3b9b470c093b3d20b7d751722c1c24f3eed2e19d
- https://github.com/axllent/mailpit
- https://pkg.go.dev/vuln/GO-2026-4284
