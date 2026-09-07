# [H] dbgate-web: Stored XSS in applicationIcon leads to potential RCE in Electron due to unsafe renderer configuration

## Summary
Severity: High
Advisory: GHSA-35xm-qvjg-8m42
CVE: CVE-2026-34725
CWE: CWE-79, CWE-94
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:R/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-04-01
Source: https://github.com/advisories/GHSA-35xm-qvjg-8m42
Type: github-advisory

## Affected
- npm: `dbgate-web` — affected >=7.0.0 <7.1.5

## Details
### Summary
A stored XSS vulnerability exists in DbGate because attacker-controlled SVG icon strings are rendered as raw HTML without sanitization. In the web UI this allows script execution in another user's browser; in the Electron desktop app this can escalate to local code execution because Electron is configured with `nodeIntegration: true` and `contextIsolation: false`.

### Details
The issue is in the icon rendering path:

- `packages/web/src/icons/FontIcon.svelte`
  - treats any icon string starting with `<svg` as inline SVG
  - renders it with `{@html iconValue}` without sanitization
- `packages/api/src/controllers/apps.js`
  - loads app definitions from disk and returns `applicationIcon` to clients unchanged
- `packages/web/src/appobj/DatabaseAppObject.svelte`
  - passes `applicationIcon` into `additionalIcons`
- `packages/web/src/appobj/AppObjectCore.svelte`
  - renders those icons through `<FontIcon icon={ic.icon}>`

This makes `applicationIcon` a stored XSS sink.

An attacker who can create or modify an app definition can store a payload in `applicationIcon`. When another user views a matching database/app entry, the payload executes in that user's session.

The impact is especially severe in Electron desktop because:

- `app/src/electron.js`
  - `nodeIntegration: true`
  - `contextIsolation: false`

With that configuration, JavaScript gained through XSS can access Node/Electron APIs, making local code execution possible.


### PoC
This was reproduced by creating an app definition with a malicious `applicationIcon` and making it match a visible database.

Example payload:

```json
{
  "applicationName": "XSS PoC",
  "applicationIcon": "<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"18\" height=\"18\"><circle cx=\"9\" cy=\"9\" r=\"8\" fill=\"red\"/></svg><img src=x onerror=\"alert('xss-fired')\">",
  "usageRules": [
    {
      "serverHostsList": ["postgres"],
      "databaseNamesList": ["dbgate"]
    }
  ]
}
```

After saving this app definition and opening the UI where the matching database/app icon is rendered, the JavaScript executes.

RCE In Electron app: 
1. Prepare an attacker-controlled application JSON file with a malicious `applicationIcon` value.
2. Set `usageRules` so the application matches a database the victim is likely to view.
3. Example payload:

```json
{
  "applicationName": "XSS PoC",
  "applicationIcon": "<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"18\" height=\"18\"><circle cx=\"9\" cy=\"9\" r=\"8\" fill=\"red\"/></svg><img src=x onerror=\"require('fs').writeFileSync(require('path').join(process.cwd(),'xss-rce-poc.txt'),'poc')\">",
  "usageRules": [
    {
      "serverHostsRegex": ".*",
      "databaseNamesRegex": ".*"
    }
  ]
}
```

4. Deliver this JSON file to the victim as an application definition file.
5. The victim imports or saves the file into DbGate's apps storage, for example by opening/creating an application file and saving the attacker-controlled JSON content.
6. DbGate later loads that app definition through apps/get-all-apps.
7. When the victim opens a UI view that renders the matching database/application icon, the applicationIcon value is passed into FontIcon.
8. FontIcon detects that the string starts with <svg and renders it via raw {@html}.
9. The injected HTML executes in the Electron renderer process.
10. Because DbGate Desktop uses nodeIntegration: true and contextIsolation: false, the payload can access Node APIs and write the marker file xss-rce-poc.txt

This demonstrates that a malicious saved application JSON file can become stored XSS in the UI and escalate to local code execution in Electron.

### Impact
**Web app**
If an attacker can place a malicious application definition where another user will load it, arbitrary JavaScript executes in the victim's browser session. This can lead to token theft, session hijacking, and performing privileged actions as the victim inside DbGate.

**Electron desktop app**
In the desktop app, the impact is more severe because the Electron renderer is configured with `nodeIntegration: true` and `contextIsolation: false`. If a victim imports or saves a malicious application definition and later opens a UI view that renders the icon, the XSS can access Node/Electron APIs and may result in local code execution on the victim machine.

## References
- https://github.com/dbgate/dbgate/security/advisories/GHSA-35xm-qvjg-8m42
- https://nvd.nist.gov/vuln/detail/CVE-2026-34725
- https://github.com/dbgate/dbgate/commit/a7d2ed11f3f3d4dfb5d2e4e5467dedafa5fa947e
- https://github.com/dbgate/dbgate
- https://github.com/dbgate/dbgate/releases/tag/v7.1.5
