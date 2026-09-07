# [H] NocoDB Vulnerable to Stored Cross-Site Scripting via SVG upload

## Summary
Severity: High
Advisory: GHSA-q5c6-h22r-qpwr
CVE: CVE-2026-24769
CWE: CWE-434, CWE-79
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:P/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H/E:P (CVSS_V4)
Published: 2026-01-28
Source: https://github.com/advisories/GHSA-q5c6-h22r-qpwr
Type: github-advisory

## Affected
- npm: `nocodb` — affected >=0 <0.301.0

## Details
## Summary

A **stored Cross-site Scripting (XSS)** vulnerability exists in NocoDB’s attachment handling mechanism. Authenticated users can upload malicious SVG files containing embedded JavaScript, which are later rendered inline and executed in the browsers of other users who view the attachment.

Because the malicious payload is stored server-side and executed under the application’s origin, successful exploitation can lead to account compromise, data exfiltration and unauthorized actions performed on behalf of affected users.

---

## Vulnerability Details

NocoDB allows file attachments to be previewed inline based on their MIME type. Due to overly permissive MIME type checks and a lack of content sanitization, SVG files containing executable JavaScript are incorrectly treated as safe image content and rendered directly in the browser.

### Root Cause

The vulnerability results from a combination of **overly permissive MIME type classification** and **unsafe file serving behavior**.

#### 1. Permissive MIME Type Check

In `attachmentHelpers.ts`, files are considered previewable if their MIME type contains certain substrings:

```ts
const previewableMimeTypes = ['image', 'pdf', 'video', 'audio'];

export const isPreviewAllowed = (args: { mimetype?: string } = {}) => {
  const { mimetype } = args;
  if (!mimetype) return false;
  return previewableMimeTypes.some((type) => mimetype.includes(type));
};
```

This substring-based check (`includes`) causes files with the MIME type `image/svg+xml` to be classified as safe for inline preview. However, SVG is an XML-based format that supports executable JavaScript via `<script>` elements, event handlers, and external references.

No additional validation or sanitization is performed on SVG content after this classification.

#### 2. Unsafe Inline File Serving

Uploaded attachments are served by the `fileReadv3` endpoint in `attachments.controller.ts` without sanitization or content-type enforcement:

```ts
@Get('/dltemp/:param(*)')
async fileReadv3(@Param('param') param: string, @Res() res: Response) {
  // No authentication guard

  // Sets headers from query parameters
  res.setHeader('Content-Type', queryParams.contentType);
  res.setHeader('Content-Disposition', queryParams.contentDisposition);

  // Sends raw file content
  res.sendFile(file.path);
}
```

The endpoint:

* Preserves the original `Content-Type` (`image/svg+xml`)
* Uses `Content-Disposition: inline`
* Sends the raw file contents unmodified

As a result, browsers render the SVG inline and execute any embedded JavaScript under the NocoDB application’s origin.

---

## Impact

This is a **stored XSS** vulnerability that can be exploited by authenticated users with permission to upload attachments.

Potential impacts include:

* Account takeover
* Theft of session cookies or API tokens
* Unauthorized actions performed on behalf of victims
* Privilege escalation if higher-privileged users view the malicious attachment

---

## Credit

This issue was discovered by an AI agent developed by the GitHub Security Lab and reviewed by GHSL team members @p- (Peter Stöckli) and @m-y-mo (Man Yue Mo).

## References
- https://github.com/nocodb/nocodb/security/advisories/GHSA-q5c6-h22r-qpwr
- https://nvd.nist.gov/vuln/detail/CVE-2026-24769
- https://github.com/nocodb/nocodb
