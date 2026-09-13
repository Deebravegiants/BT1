# [H] Fluentd is Vulnerable to Exposure of Sensitive Information via Monitor Agent API

## Summary
Severity: High
Advisory: GHSA-pr7j-96cj-549h
CVE: CVE-2026-44025
CWE: CWE-200, CWE-306
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-06-26
Source: https://github.com/advisories/GHSA-pr7j-96cj-549h
Type: github-advisory

## Affected
- RubyGems: `fluentd` — affected >=0 <1.19.3

## Details
Fluentd's Monitor Agent plugin (`in_monitor_agent`) exposes internal metrics and plugin information via a REST API.
It was discovered that the API response (`/api/plugins.json` and related endpoints) unintentionally includes internal instance variables of loaded plugins.

If any plugins store sensitive information—such as database passwords, API keys, or cloud credentials—in its instance variables,
this information may be exposed in plain text to any user or system that has HTTP access to the Monitor Agent API.

### Impact
This vulnerability allows for unauthorized information disclosure. An attacker who can reach the Monitor Agent API port (default: `24220`) can potentially extract sensitive credentials used by other Fluentd plugins.
The impact severity depends highly on the network configuration (whether the Monitor Agent port is exposed to untrusted networks) and the specific plugins configured in the Fluentd instance.

### Patches:
v1.19.3

### Workarounds
If usesrs cannot immediately update Fluentd to the patched version, they can mitigate this risk by strictly controlling access to the Monitor Agent port.

Ensure the Monitor Agent is only bound to `localhost` (`127.0.0.1`) rather than `0.0.0.0`.

```
<source>
  @type monitor_agent
  bind 127.0.0.1
  port 24220
</source>
```

Use firewall rules (e.g., iptables, AWS Security Groups) to block access to the Monitor Agent port (`24220`) from untrusted networks or instances.

## References
- https://github.com/fluent/fluentd/security/advisories/GHSA-pr7j-96cj-549h
- https://github.com/fluent/fluentd
- https://github.com/fluent/fluentd/releases/tag/v1.19.3
