# [H] Gitea: Stored XSS via glTF `extensionsRequired` in Gitea 3D File Viewer

## Summary
Severity: High
Advisory: GHSA-9cpj-qc93-vw8v
CVE: CVE-2026-28737
CWE: CWE-79
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2026-06-17
Source: https://github.com/advisories/GHSA-9cpj-qc93-vw8v
Type: github-advisory

## Affected
- Go: `code.gitea.io/gitea` — affected >=1.25.0 <1.26.0

## Details
## Summary

Me again.

Gitea's built-in 3D file viewer (powered by Online3DViewer) is vulnerable to stored cross-site scripting (XSS) through crafted `.gltf` files. When a glTF file declares an unsupported required extension, Online3DViewer generates an error message containing the extension name and Gitea inserts it into the DOM using `innerHTML` without sanitization. An attacker who can push a `.gltf` file to any repository can execute arbitrary JavaScript in the context of any user who views the file.

## Affected Versions

- Gitea **1.25.0** and later (3D file preview was introduced in 1.25 via the Online3DViewer integration)
- Confirmed on `gitea:1.25-nightly` (SHA `e33d1da...`), which bundles `online-3d-viewer` npm package v0.16.0
- The upstream [Online3DViewer](https://github.com/kovacsv/Online3DViewer) library is the root cause

## Severity

- Stored XSS: the payload persists in the repository and fires on every page view
- Executes under the Gitea origin with the victim's session (cookies, CSRF tokens)
- Any authenticated user viewing the file is compromised
- Enables full account takeover (token creation, settings modification, repository manipulation)
- No user interaction beyond viewing the file page is required

## Details

### Root Cause

When Online3DViewer parses a glTF file, it checks whether all `extensionsRequired` entries are supported. For unsupported extensions, it calls:

```javascript
// In the Online3DViewer bundle (online-3d-viewer.js)
// Approximate offset 1142618 in the bundled chunk
this.SetError(yp("Unsupported extension: {0}.", unsupportedExtensions.join(", ")));
```

The `SetError` method stores this message, and Gitea's rendering code inserts it into the page using `innerHTML`:

```javascript
// Gitea's error display handler
element.innerHTML = errorMessage;  // unsanitized
```

The extension names from `extensionsRequired` are taken directly from the JSON file with no escaping or sanitization, allowing HTML injection.

### Attack Vector

1. An attacker creates a `.gltf` file with a malicious `extensionsRequired` value:

```json
{
  "asset": {"version": "2.0"},
  "buffers": [],
  "extensionsRequired": ["<img src=x onerror=\"alert(document.cookie)\">"],
  "scenes": []
}
```

2. The attacker pushes this file to any Gitea repository they have write access to (including forks of public repositories).

3. When any user navigates to the file's page in the Gitea web UI, the 3D viewer attempts to render it, encounters the "unsupported extension," and inserts the error message (containing the attacker's HTML) into the DOM via `innerHTML`.

4. The injected `<img onerror>` handler executes arbitrary JavaScript under the Gitea origin with the victim's authenticated session.

### Impact

From the XSS context, an attacker can:

- **Create API access tokens** for the victim by POSTing to `/user/settings/applications` with the page's CSRF token
- **Read private repositories** via same-origin API calls
- **Modify repository contents** (supply chain attacks)
- **Escalate to admin** if the victim is a Gitea administrator
- **Exfiltrate data** via `fetch`, `XMLHttpRequest`, or `navigator.sendBeacon`

## Proof of Concept

### Minimal PoC (alert box)

Save as `poc.gltf` and push to any Gitea 1.25+ repository:

```json
{
  "asset": {"version": "2.0"},
  "buffers": [],
  "extensionsRequired": ["<img src=x onerror=\"alert('XSS: '+document.domain)\">"],
  "scenes": []
}
```

Navigate to the file in the Gitea web UI. The alert will fire.


## Suggested Fixes

Sanitize or text-encode the error message before DOM insertion. Replace `innerHTML` with `textContent` for error display:

```javascript
// Instead of:
element.innerHTML = errorMessage;

// Use:
element.textContent = errorMessage;
```

Alternatively, escape HTML entities in the error message before insertion.

### Additional hardening

- Render 3D file previews inside a sandboxed `<iframe>` with `sandbox="allow-scripts"` and a restrictive CSP (`default-src 'none'`), similar to how Gitea already handles SVG attachments
- Apply Content-Security-Policy headers to file preview pages that restrict inline script execution

## References
- https://github.com/go-gitea/gitea/security/advisories/GHSA-9cpj-qc93-vw8v
- https://github.com/go-gitea/gitea
