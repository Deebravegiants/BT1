# [M] LF Edge eKuiper: SSRF in External Service

## Summary
Severity: Medium
Advisory: GHSA-pqqc-8v73-9gg2
Aliases: CVE-2025-24979
Ecosystem: Go
Published: 2026-09-09
Source: https://osv.dev/vulnerability/GHSA-pqqc-8v73-9gg2
Type: osv

## Affected
- Go: `github.com/lf-edge/ekuiper/v2` — affected >=0 <2.4.0

## Details
### Summary
Server-side request forgery (SSRF) vulnerability in eKuiper allows an attacker with permissions to register external services or create rules to induce the eKuiper server to make requests to unintended network locations, such as internal services, loopback interfaces (localhost), or cloud metadata endpoints.

### Details
Prior to v2.4.0, eKuiper external service registrations and HTTP invocations did not validate destination IP addresses. An attacker with access to the eKuiper management API could register an external service pointing to an internal address (such as `http://127.0.0.1:9081` or other internal network services) and trigger queries using service functions (e.g. `SELECT tsschemaless(...) FROM demo`). This allows probing internal networks, leaking sensitive information (such as internal endpoints/credentials), or interacting with internal APIs accessible to the eKuiper host.

### PoC
1. Create an external service with an address pointing to an internal network / localhost:

```json
{
  "interfaces": {
    "tsschemaless": {
      "address": "http://127.0.0.1:9081",
      "protocol": "rest",
      "options": {
        "insecureSkipVerify": true,
        "headers": {
          "Accept-Charset": "utf-8"
        }
      },
      "schemaless": true
    }
  }
}
```
2. Load it to eKuiper and create a rule invoking it, e.g.: `SELECT tsschemaless("get", "/metadata/sources/yaml/mqtt", *) FROM demo`.
3. Run the rule. When data flows through the stream, the response from the internal service is retrieved and can be routed to an external sink or inspected.

### Impact
Server-Side Request Forgery (SSRF) allowing unauthorized access / probing of internal network services.

### Remediation & Patches
- **Upgrade to eKuiper >= 2.4.0**: Starting with v2.4.0, SSRF protection (`httpx.GetSSRFDialContext`) is enabled by default across HTTP clients, blocking requests to private, loopback, link-local, multicast, and unspecified IP addresses.

### Workarounds (for versions < 2.4.0)
If unable to upgrade immediately:
1. **Restrict Management API Access**: Restrict access to the eKuiper REST API (port 9081) and CLI using network firewalls, reverse proxies, and authentication so only trusted administrators can create or update services and rules.
2. **Egress Network Filtering**: Use firewall / iptables rules or container network isolation to block outbound requests from eKuiper to private subnets, loopback addresses, and cloud metadata endpoints (`169.254.169.254`).
3. **Audit Service Definitions**: Regularly review registered external services (`GET /services` or `bin/kuiper show services`) to verify target hosts.

### Notes for Users Upgrading to >= 2.4.0
- In v2.4.0 and later, `basic.enablePrivateNet` in `kuiper.yaml` defaults to `false` (blocking private network access).
- If a developer's deployment legitimately requires eKuiper to communicate with internal REST services or private networks, they can explicitly opt in by setting `basic.enablePrivateNet: true` (or via environment variable `KUIPER__BASIC__ENABLEPRIVATENET=true`). Ensure eKuiper's API is protected before enabling this setting.

Reported by Alexey Kosmachev, Bi.Zone

## References
- https://github.com/lf-edge/ekuiper/security/advisories/GHSA-pqqc-8v73-9gg2
- https://github.com/lf-edge/ekuiper
- https://github.com/lf-edge/ekuiper/releases/tag/v2.4.0
