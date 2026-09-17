# [M] Unleash: Global Mustache.escape override disables HTML escaping process-wide, enabling Slack/Teams link-injection via unrestricted username

## Summary
Severity: Medium
Advisory: GHSA-w4mq-xh27-6xpx
CVE: CVE-2026-63466
CWE: CWE-116
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:N/I:L/A:N (CVSS_V3)
Published: 2026-08-21
Source: https://github.com/advisories/GHSA-w4mq-xh27-6xpx
Type: github-advisory

## Affected
- npm: `unleash-server` — affected >=0 <8.0.3

## Details
## Vulnerability Details

**File**: `src/lib/addons/feature-event-formatter-md.ts`
**Line**: 355 (in v8.0.1; `format()` method)

### Root Cause

`FeatureEventFormatterMd.format()` does:

```ts
Mustache.escape = (text) => text;
const text = Mustache.render(action, context);
```

`mustache` (pinned `^4.2.0`, confirmed installed `4.2.0`) keeps `escape` as a **module-level singleton** (`mustache.js`: `mustache.escape = escapeHtml;`), read by every `Mustache.render()` call in the process unless a per-call `config.escape` override is passed (`var escape = this.getConfigEscape(config) || mustache.escape;`). Node's module cache guarantees every `import Mustache from 'mustache'` in the process — `feature-event-formatter-md.ts`, `email-service.ts`, `webhook.ts`, `datadog.ts`, `new-relic.ts` — shares the same object instance.

This assignment therefore **permanently disables HTML escaping for every other `Mustache.render()` call in the same Node process** (including `email-service.ts` templates) from the moment any single notification addon (Webhook, Slack legacy, Microsoft Teams, Datadog, New Relic) first formats any event, for the remaining lifetime of the process.

`feature-event-formatter-md-events.ts` (`EVENT_MAP`) confirms the blast radius: nearly every event's `action` template interpolates attacker-controlled values with single-mustache (intended-to-be-escaped) syntax, most importantly `{{user}}`, which is `event.createdBy` — the acting account's `username` (or `email` if set; `src/lib/util/extract-user.ts`: `extractUsernameFromUser`). Neither `username` nor `name` have any charset/length validation anywhere in the codebase (`create-user-schema.ts`, `create-invited-user-schema.ts`, `user-service.ts:289` only does `Joi.assert(name, Joi.string(), 'Name')` — a type check, nothing more).

Slack's own API docs require `&`, `<`, `>` to be replaced with `&amp;`, `&lt;`, `&gt;` before sending user-generated text, specifically so Slack's mrkdwn parser does not interpret it as `<url|label>` link syntax. Mustache's default `escapeHtml` happens to produce exactly those entities, so this was (likely unintentionally) the application's only defense against link-injection in chat notifications — and it is unconditionally switched off by the same code path that depends on it.

### Attack Scenario
1. Admin has a Webhook, Slack (legacy), Microsoft Teams, Datadog, or New Relic integration configured (a very common production setup for flag-change notifications).
2. Attacker has (or self-registers, if public signup is enabled — `POST /invite/:token/signup` is `permission: NONE`) any **Editor**-level account and sets `username` to e.g. `evil<https://attacker.example/urgent-rollback|Click here to view incident>`.
3. Attacker performs any ordinary write action (create/update/toggle a feature flag — routine, no special privilege beyond Editor on one project).
4. The configured addon's `handleEvent()` calls `this.msgFormatter.format(event)`, which mutates the global escape function and immediately renders the `{{user}}`-containing template with escaping disabled.
5. The resulting message — containing the attacker's raw `<url|label>` Slack link syntax — is POSTed to the team's Slack/Teams channel or webhook endpoint and rendered as a real, clickable, attacker-labeled hyperlink inside a trusted automated notification feed.

### Vulnerable Code
```ts
Mustache.escape = (text) => text;

const text = Mustache.render(action, context);
const url = path
    ? `${this.unleashUrl}${Mustache.render(path, context)}`
    : undefined;
```

### Impact
- Stored markdown/link-injection (phishing-link injection) into any configured outbound notification channel (Slack legacy, MS Teams, Webhook default markdown, Datadog, New Relic), using an attacker-controlled username — no admin privilege required, only Editor on a single project, and potentially reachable through public self-signup.
- Secondary: loss of HTML escaping for any other reachable Mustache single-mustache placeholder process-wide until restart (increases severity of any other currently-unreached or future Mustache sink, e.g. email templates).
- Tertiary: a custom Webhook `bodyTemplate` that interpolates raw event/user fields directly into a JSON string literal (rather than the pre-escaped `eventJson` field the code already provides for this purpose) can have its JSON structure broken by an attacker-controlled `"` character once the global escape function is neutered.

### Recommended Fix
Never mutate the shared `Mustache.escape` global. Pass a local escape function via Mustache's per-call render option instead (supported and typed in `@types/mustache@4.2.6`'s `RenderOptions.escape`):

```ts
const renderConfig = { escape: (text: string) => text };
const text = Mustache.render(action, context, undefined, renderConfig);
const url = path
    ? `${this.unleashUrl}${Mustache.render(path, context, undefined, renderConfig)}`
    : undefined;
```

### Verification
Dynamically confirmed on v8.0.1 in a local Docker lab (official `unleashorg/unleash-server:8.0.1` image + Postgres 15):
- Created a Webhook addon with the addon UI's own placeholder `bodyTemplate` (`{{event.createdBy}}` etc.), pointed at a local listener.
- Created an Editor-role user with `username = evil2<https://attacker.example/urgent-rollback|Click here to view incident>` (accepted with HTTP 201, no sanitization).
- Logged in as that user and created a feature flag (ordinary Editor action).
- Captured webhook payload: `"createdBy": "evil2<https://attacker.example/urgent-rollback|Click here to view incident>"` — `<`, `>`, `|` completely unescaped, live Slack link-injection syntax.
- Control test with the same pinned `mustache@4.2.0` package confirmed the default (pre-bug) output for the same string would have been `evil2&lt;https:&#x2F;&#x2F;attacker.example&#x2F;urgent-rollback|Click here to view incident&gt;` — i.e. the single global assignment is solely responsible for the unescaped output observed live.

## References
- https://github.com/Unleash/unleash/security/advisories/GHSA-w4mq-xh27-6xpx
- https://github.com/Unleash/unleash/commit/002012cfdbedd2e9b7db9dc83b9f549f761db22e
- https://github.com/Unleash/unleash
- https://github.com/Unleash/unleash/releases/tag/v8.0.3
