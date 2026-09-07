# [M] Open WebUI has Stored XSS in Pending User Overlay via Incorrect DOMPurify Application Order

## Summary
Severity: Medium
Advisory: GHSA-fq3v-xjjx-95rc
CVE: CVE-2026-44568
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-05-08
Source: https://github.com/advisories/GHSA-fq3v-xjjx-95rc
Type: github-advisory

## Affected
- PyPI: `open-webui` — affected >=0 <0.9.0

## Details
## Vulnerability Details

**CWE-79**: Cross-site Scripting (XSS)

The `AccountPending.svelte` component renders the admin-configured "Pending User Overlay Content" using `marked.parse()` inside `{@html}` with an incorrect DOMPurify application order:

### Vulnerable Code

**`src/lib/components/layout/Overlay/AccountPending.svelte` (lines 43-48)**:

```svelte
{@html marked.parse(
    DOMPurify.sanitize(
        ($config?.ui?.pending_user_overlay_content ?? '').replace(/\n/g, '<br>')
    )
)}
```

DOMPurify is applied to the raw Markdown input **before** `marked.parse()` processes it. This is the wrong order. DOMPurify sanitizes the Markdown text (which contains no HTML tags), then `marked.parse()` converts Markdown link syntax into HTML `<a>` tags with `javascript:` href, and the result is rendered with `{@html}` unsanitized.

The correct pattern (used elsewhere in the codebase, e.g., `NotebookView.svelte:77`) is:
```javascript
DOMPurify.sanitize(marked.parse(src))  // sanitize AFTER markdown parsing
```

## Steps to Reproduce

### Prerequisites
- Open WebUI v0.8.10
- Admin account
- A second user account with "pending" role

### Steps

1. Log in as admin and navigate to **Admin Settings** → **Settings** → **General**.

2. Set **Default User Role** to `pending`.

3. In the **Pending User Overlay Content** field, enter:
```
# Account Pending

Your account is under review.

[Contact Support](javascript:alert(document.domain))
```

4. Save the settings.

5. In a separate browser (or incognito window), create a new account or log in as a pending user.

6. The pending overlay is displayed. Click the "Contact Support" link.

7. A JavaScript alert dialog appears showing `localhost` (the document domain), confirming XSS execution.

### Verified Output

The `alert(document.domain)` executes successfully, displaying "localhost" in a JavaScript dialog box.

## Impact

An admin can inject arbitrary JavaScript into the Pending User Overlay Content that executes in the browser context of any pending user who views the overlay page. This could be used to:

- **Session hijacking**: Steal pending users' JWT tokens from cookies/localStorage
- **Credential theft**: Replace the pending overlay with a fake login form
- **Phishing**: Redirect pending users to malicious sites

While this requires admin privileges to set the overlay content, it enables an admin to attack pending users (who have not yet been granted full access). In multi-admin deployments, a compromised admin account could use this to escalate attacks.

## Proposed Fix

Apply DOMPurify **after** `marked.parse()`, not before:

```svelte
<!-- Before (vulnerable): -->
{@html marked.parse(
    DOMPurify.sanitize(
        ($config?.ui?.pending_user_overlay_content ?? '').replace(/\n/g, '<br>')
    )
)}

<!-- After (fixed): -->
{@html DOMPurify.sanitize(
    marked.parse(
        ($config?.ui?.pending_user_overlay_content ?? '').replace(/\n/g, '<br>'),
        { async: false }
    )
)}
```
<img width="1510" height="1093" alt="2026-03-23_03-07" src="https://github.com/user-attachments/assets/bcc94dd6-4f06-472b-9979-9759458c76b3" />

## References
- https://github.com/open-webui/open-webui/security/advisories/GHSA-fq3v-xjjx-95rc
- https://nvd.nist.gov/vuln/detail/CVE-2026-44568
- https://github.com/open-webui/open-webui
