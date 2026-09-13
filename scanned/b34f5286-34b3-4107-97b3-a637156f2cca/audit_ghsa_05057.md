# [H] Nodemailer: Message-level raw option bypasses disableFileAccess/disableUrlAccess, enabling arbitrary file read and full-response SSRF in the delivered message

## Summary
Severity: High
Advisory: GHSA-p6gq-j5cr-w38f
CVE: CVE-2026-82659
CWE: CWE-73, CWE-918
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2026-06-18
Source: https://github.com/advisories/GHSA-p6gq-j5cr-w38f
Type: github-advisory

## Affected
- npm: `nodemailer` — affected >=0 <9.0.1

## Details
# Message-level `raw` option bypasses `disableFileAccess` / `disableUrlAccess`, enabling arbitrary file read and full-response SSRF in the sent message

- **Target:** nodemailer/nodemailer, npm `nodemailer` **v9.0.0** (HEAD `4e58450eb490e5097a74b2b2cce35a8d9e21856e`)
- **Verdict:** CONFIRMED (local PoC, no network)

## Summary

Nodemailer exposes `disableFileAccess` and `disableUrlAccess` so an application that passes
**untrusted** message data to the library can forbid that data from reading local files or
fetching URLs. Every attachment, alternative, `html`/`text`/`watchHtml`/`amp` and `icalEvent`
content node honors these flags. **The message-level `raw` option does not.**

`MailComposer.compile()` builds the root MIME node for a `raw` message **without** threading the
two flags, so a `raw: { path: '/etc/passwd' }` or `raw: { href: 'http://169.254.169.254/…' }`
message is read / fetched anyway, and the file or HTTP-response bytes become the **actual
message that is sent** by every transport (SMTP, SES, sendmail, stream, JSON). An actor whose
input the application intended to sandbox therefore obtains arbitrary local-file disclosure and
a full-response SSRF primitive, delivered to a recipient the same actor can choose.

This is the same vulnerability class as the already-published jsonTransport advisory
**GHSA-wqvq-jvpq-h66f**, but a **distinct code path** (`raw` root node, not `normalize()`), and
strictly higher impact: the jsonTransport bug only affected the locally-returned JSON, whereas
this affects the delivered RFC822 message for all transports.

## Affected component

- `lib/mail-composer/index.js:34-35` — root cause:
  ```js
  if (this.mail.raw) {
      this.message = new MimeNode('message/rfc822', { newline: this.mail.newline }).setRaw(this.mail.raw);
  }
  ```
  The `MimeNode` is constructed with only `{ newline }`. Compare the sibling node builders
  `_createMixed`/`_createAlternative`/`_createRelated`/`_createContentNode`
  (`lib/mail-composer/index.js:389-527`), which all pass
  `disableUrlAccess: this.mail.disableUrlAccess, disableFileAccess: this.mail.disableFileAccess`.
- `lib/mime-node/index.js:51-52` — the constructor derives `this.disableFileAccess`/
  `this.disableUrlAccess` solely from its own `options`; children do **not** inherit a parent's
  flags (`createChild`/`appendChild`, lines 175-194, pass options through verbatim).
- `lib/mime-node/index.js:812` — `setRaw()` content is resolved through `this._getStream(this._raw)`.
- `lib/mime-node/index.js:984-1010` — `_getStream` reads the file (`fs.createReadStream`, 995) or
  fetches the URL (`nmfetch`, 1009) **only guarded by `this.disableFileAccess`/`this.disableUrlAccess`**,
  which on the `raw` root node are `false`.
- Reached from the normal send flow at `lib/mailer/index.js:188`
  (`mail.message = new MailComposer(mail.data).compile()`), so every transport is affected.

## Reachability gate (hop-by-hop)

1. **Source.** Application calls `transporter.sendMail({ raw: <userControlled> , to: <userControlled> })`
   with `disableFileAccess: true` and/or `disableUrlAccess: true` configured on the transporter
   (forced onto `mail.data` in `lib/mailer/mail-message.js:36-40`) or per message. This is the
   exact scenario the flags exist for — the same precondition under which GHSA-wqvq-jvpq-h66f was
   accepted.
2. **Guard — the access flags.** For attachments the flag is enforced: a node created by
   `_createContentNode` carries `disableFileAccess`, so `_getStream` throws `EFILEACCESS`.
   **Bypass:** the `raw` branch (`compile():34-35`) never sets the flag on its node, so
   `this.disableFileAccess === false` and the guard at `mime-node:985` / `:999` is skipped.
   There is no other validation between `mail.raw` and the read; `raw` content shapes
   (`{path}`, `{href}`, stream, string, buffer) are accepted as-is by `setRaw`/`_getStream`.
3. **Sink.** `fs.createReadStream(content.path)` (file disclosure) or
   `nmfetch(content.href, …)` (SSRF). The resulting bytes are emitted as the message body by
   `createReadStream()`, which every transport pipes to its destination
   (`smtp-transport:233`, `smtp-pool/pool-resource:208`, `ses-transport:96`, `sendmail-transport:184`,
   `stream-transport:67`).

No guard blocks the chain; the only guard (the access flags) is structurally absent on this node.

## Root cause

Inconsistent enforcement: the access policy is applied per-`MimeNode` via constructor options and
must be re-passed at every node creation. The `raw`-message shortcut in `compile()` omits it,
while all five other node builders include it. The flags are therefore enforced for every content
type *except* the one that lets the caller supply a complete message body by path/URL.

## Exploit path

Application that sandboxes untrusted mail input (`disableFileAccess`/`disableUrlAccess` set):

1. Untrusted actor supplies `raw: { path: '/proc/self/environ' }` (or any server file:
   `/app/.env`, key material, etc.) and `to: attacker@evil.test`.
2. `compile()` builds the raw root node without the flags; the transport reads the file and sends
   its contents as the message → **arbitrary server-file exfiltration to an attacker-chosen mailbox.**
3. Alternatively `raw: { href: 'http://127.0.0.1:8080/admin' }` or a cloud metadata URL →
   Nodemailer fetches it server-side and delivers the full response body in the email →
   **full-response SSRF** (no blind-channel limitation).

## Impact

- **Confidentiality (High):** arbitrary local file read disclosed in the outgoing message;
  full-response SSRF to internal/metadata endpoints, also disclosed in the message.
- **Integrity (Low):** attacker-fetched/file content is injected into the delivered mail.
- The two protective flags an application relies on to contain untrusted input are silently
  ineffective for `raw`.

## Preconditions

The application (a) passes `disableFileAccess` and/or `disableUrlAccess` (the documented sandboxing
flags) and (b) lets untrusted input influence the `raw` field (and, for maximal disclosure, `to`).
No other configuration is required; all bundled transports are affected. This mirrors the accepted
precondition of GHSA-wqvq-jvpq-h66f.

## Severity

- **AV** — message data routinely originates over the network in the apps these flags protect.
- **AC** — a single crafted `raw` object; deterministic.
- **PR** — the actor is a user whose input the app already treats as untrusted (the reason the
  flags are set); not fully anonymous in the typical deployment.
- **UI** — no victim interaction.
- **S** — impact within Nodemailer's process scope.
- **C** — arbitrary file read **and** full-response SSRF, both delivered to an attacker-chosen
  recipient. (The sibling jsonTransport advisory used C:L because its leak stayed in locally-returned
  JSON; here the bytes leave the system in the sent message, so C:H is warranted.)
- **I** — attacker injects fetched/file bytes into the outgoing message.
- **A**.
Note: if a deployment fixes the recipient (`to` not attacker-controlled) the disclosure channel
narrows and the rating degrades toward the sibling's Medium; the High rating reflects the
reasonable worst case where `raw` and `to` are both untrusted.

## Adversarial re-read (attempts to refute)

1. **"`raw` content is by-design trusted, so the flags shouldn't apply."** Rejected: every other
   content path (attachments, alternatives, html/text, icalEvent) honors the flags, and the
   maintainer already accepted GHSA-wqvq-jvpq-h66f for exactly this "untrusted input + flag set"
   model. The asymmetry — attachment `{path}` is blocked but `raw:{path}` is not — is the bug, and
   the PoC's CONTROL case proves the flag is otherwise effective on the same file.
2. **"The raw node inherits the flags via rootNode."** Rejected by code and by PoC: `compile():35`
   constructs the node with `{ newline }` only; `MimeNode` constructor sets
   `this.disableFileAccess = !!options.disableFileAccess` → `false`; `rootNode` is itself; no
   inheritance exists.
3. **"The PoC leaks for an unrelated reason."** Rejected: the CONTROL message (`attachments:[{path}]`,
   same file, same transporter) returns `EFILEACCESS`; only the `raw:{path}` message leaks. The
   sentinel nonce exists solely in the temp file; the URL nonce is generated server-side and is only
   obtainable by an actual fetch. Both observables are uniquely bound to the bypass.
4. **"Maybe only jsonTransport (already reported) is affected."** Rejected: the PoC uses
   `streamTransport` and the root cause is in `MailComposer.compile()` (`mailer:188`), shared by all
   transports; jsonTransport is a different (already-fixed) path.

I could not find any guard that blocks the chain; the finding survives.

## Proof of concept (safe, benign)

`findings/nodemailer/raw/poc-raw-fileaccess-bypass.js` — local, no network egress (loopback only),
no destructive action. Output:
```
[CONTROL] attachment path with disableFileAccess: BLOCKED (EFILEACCESS) — flag works here
[ATTACK]  raw:{path} with disableFileAccess=true: BYPASSED — sentinel file CONTENT present in message
[ATTACK]  raw:{href} with disableUrlAccess=true (loopback server): BYPASSED — fetched body present (SSRF)
VERDICT: CONFIRMED
```
Run: `node findings/nodemailer/raw/poc-raw-fileaccess-bypass.js` (exit 0 = confirmed).

## Remediation

Thread the access policy onto the `raw` root node, exactly as the other builders do:
```js
if (this.mail.raw) {
    this.message = new MimeNode('message/rfc822', {
        newline: this.mail.newline,
        disableFileAccess: this.mail.disableFileAccess,
        disableUrlAccess: this.mail.disableUrlAccess
    }).setRaw(this.mail.raw);
}
```
(Defense in depth: `setRaw`/`_getStream` could also refuse `{path}`/`{href}` raw content when either
flag is set, regardless of how the node was constructed.) Add a regression test asserting that
`raw:{path}` and `raw:{href}` reject with `EFILEACCESS`/`EURLACCESS` when the flags are set, mirroring
the attachment tests.

## References
- https://github.com/Sif-0x01/security-advisories/security/advisories/GHSA-68x8-4h5v-r533
- https://github.com/nodemailer/nodemailer/security/advisories/GHSA-p6gq-j5cr-w38f
- https://nvd.nist.gov/vuln/detail/CVE-2026-82659
- https://github.com/nodemailer/nodemailer/commit/a82e060d978f27e5f41369a9a9807b1e3dedc2e2
- https://github.com/nodemailer/nodemailer
- https://github.com/nodemailer/nodemailer/releases/tag/v9.0.1
- https://www.vulncheck.com/advisories/nodemailer-before-9.0.1-file-read-and-ssrf-via-raw-option
