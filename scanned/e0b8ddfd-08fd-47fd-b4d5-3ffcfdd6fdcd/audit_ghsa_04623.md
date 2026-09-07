# [M] Nodemailer jsonTransport bypasses disableFileAccess and disableUrlAccess during message normalization

## Summary
Severity: Medium
Advisory: GHSA-wqvq-jvpq-h66f
CWE: CWE-862
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2026-06-15
Source: https://github.com/advisories/GHSA-wqvq-jvpq-h66f
Type: github-advisory

## Affected
- npm: `nodemailer` — affected >=0 <8.0.9

## Details
### Summary

Nodemailer's `disableFileAccess` and `disableUrlAccess` options are intended to prevent message content and attachments from reading local files or fetching URLs. The normal MIME streaming path enforces those options in `MimeNode._getStream()`. However, `jsonTransport` serializes messages by calling `mail.normalize()`, which resolves `html`, `text`, alternatives, calendar events, and attachments through `shared.resolveContent()` before MIME generation. `shared.resolveContent()` reads local files and fetches HTTP(S) URLs directly, without receiving or checking `disableFileAccess` or `disableUrlAccess`.

As a result, applications that use `jsonTransport` as a safe serializer or queue payload generator while relying on `disableFileAccess` / `disableUrlAccess` can still be made to read local files into the generated JSON output or make outbound HTTP requests when an attacker controls message content fields such as attachment `path` or `text.href`.

The same missing-enforcement root cause is also reachable before normal streaming when `attachDataUrls` causes `_convertDataImages()` to call `mail.resolveContent(mail.data, 'html', ...)`; this should be fixed with the same access-control check.

### Details
Source-to-sink evidence:

- `lib/nodemailer.js:42-45` selects `JSONTransport` when `createTransport({ jsonTransport: true, ... })` is used.
- `lib/mailer/mail-message.js:34-39` copies transport-level `disableFileAccess` and `disableUrlAccess` options into `mail.data`.
- `lib/json-transport/index.js:52-76` serializes mail by calling `mail.normalize((err, data) => ...)`.
- `lib/mailer/mail-message.js:46-135` implements `resolveAll()` and calls `shared.resolveContent(...args, ...)` for `html`, `text`, `watchHtml`, `amp`, `icalEvent`, alternatives, and attachments.
- `lib/shared/index.js:506-562` implements `resolveContent()`.
- `lib/shared/index.js:540-541` fetches HTTP(S) content with `nmfetch(content.path || content.href)`.
- `lib/shared/index.js:549-550` reads local files with `fs.createReadStream(content.path)`.
- `shared.resolveContent()` does not check `disableFileAccess` or `disableUrlAccess` and does not receive those flags.

Control path showing intended enforcement:

- `lib/mail-composer/index.js:358-359`, `lib/mail-composer/index.js:367-368`, and sibling child-node creation paths pass `disableUrlAccess` and `disableFileAccess` into `MimeNode`.
- `lib/mime-node/index.js:51-52` stores those flags.
- `lib/mime-node/index.js:984-995` rejects file paths with `EFILEACCESS` when `disableFileAccess` is set.
- `lib/mime-node/index.js:998-1009` rejects URLs with `EURLACCESS` when `disableUrlAccess` is set.
- `test/mail-composer/mail-composer-test.js:1028-1044` includes a normal MIME-streaming test that expects file access to be blocked when `disableFileAccess: true`.

Additional same-root-cause variant:

- `lib/mailer/index.js:406-434` implements `_convertDataImages()` for `attachDataUrls`.
- `lib/mailer/index.js:407-410` calls `mail.resolveContent(mail.data, 'html', ...)` when `attachDataUrls` is enabled and `mail.data.html` is present.
- Because `mail.resolveContent()` delegates to `shared.resolveContent()` at `lib/mailer/mail-message.js:42-44`, an object-form `html: { path: ... }` or `html: { href: ... }` can be resolved before the later MIME streaming enforcement sees the content.
- This variant requires `attachDataUrls` to be enabled, so the main reportable default/common path is `jsonTransport`; both should be fixed by enforcing access flags inside the pre-resolution helper or passing policy into it.

Default/common exposure evidence:

- `jsonTransport` is a shipped runtime transport selected by public `createTransport` options.
- `test/json-transport/json-transport-test.js:9-83` demonstrates that `jsonTransport` intentionally resolves file-backed `html` and attachments into JSON output.
- `disableFileAccess` and `disableUrlAccess` are documented by code and tests as security controls and are copied from transport options into message data for all transports.
- The bypass does not require test-only code, external infrastructure, unsupported configuration, or maintainer-only APIs.

False-positive screening and negative controls:

- The local PoC used the same `disableFileAccess: true` and `disableUrlAccess: true` transport options for both `jsonTransport` and normal `streamTransport` controls.
- `jsonTransport` read the temporary local fixture file and embedded the content in JSON despite `disableFileAccess: true`.
- `streamTransport` with the same attachment and `disableFileAccess: true` rejected with `EFILEACCESS`.
- `jsonTransport` fetched a local HTTP listener despite `disableUrlAccess: true`.
- `streamTransport` with the same URL and `disableUrlAccess: true` rejected with `EURLACCESS`.
- The local URL proof used only `127.0.0.1` and did not contact external infrastructure.

Affected version evidence and uncertainty:

- Confirmed vulnerable: `nodemailer` 8.0.8 at commit `15138a84c543c20aa399218534cdbbfa2ea1ce55`.
- Git history shows `jsonTransport` has existed since commit `d78b63b` (2017-02-09, "Added test for json transport"), and `disableFileAccess` appears in historical setup commit `6218b8d` (2017-01-31), but older versions were not dynamically tested during this audit.
- Affected range is therefore recorded as unknown beyond the confirmed current version.
- No patched version was identified in this checkout.

Severity rationale:

- AV: The vulnerable library path is typically reached through an application-level message submission or rendering/queueing feature.
- AC: A single message field using `path` or `href` triggers the bypass when `jsonTransport` is used.
- PR: Conservative assumption that the attacker is a lower-privileged user of an application that accepts partially user-controlled message objects. Some deployments may expose this unauthenticated, but that was not assumed.
- UI: No user interaction is required after the application accepts the message object.
- S: The impact remains in the embedding application/library security scope.
- C: Local file contents can be copied into the generated JSON output when the application later stores, logs, returns, or forwards that JSON.
- I: The attacker can induce outbound HTTP requests to attacker-chosen or internal URLs from the application host when URL access was intended to be disabled.
- A: No availability impact was demonstrated; the PoC used bounded local files and a localhost listener only.

Final self-review:

- Reproduction evidence was generated locally from this checkout using only a temporary file under the OS temp directory and a local `127.0.0.1` HTTP listener.
- The PoC included positive proof for file read and URL fetch, plus negative controls showing normal `streamTransport` rejects the same inputs with `EFILEACCESS` and `EURLACCESS`.
- The proof is non-destructive, performs no external network traffic, and deletes its temporary fixture.
- Reachability, package exposure, policy-enforcement bypass, same-root-cause variant, and false-positive controls were checked as described above.
- The affected range is not overclaimed; only the current tested version is confirmed vulnerable.

### PoC

From a clean checkout of `nodemailer` at commit `15138a84c543c20aa399218534cdbbfa2ea1ce55`, run:

```bash
node <<'NODE'
'use strict';
const fs = require('fs');
const os = require('os');
const path = require('path');
const http = require('http');
const nodemailer = require('./');
const marker = 'NM_JSON_BYPASS_' + Date.now();
const fixture = path.join(os.tmpdir(), 'nodemailer-json-bypass-' + process.pid + '.txt');
fs.writeFileSync(fixture, marker);
function sendMail(transport, data) {
  return new Promise((resolve, reject) => transport.sendMail(data, (err, info) => err ? reject(err) : resolve(info)));
}
(async () => {
  const jsonTransport = nodemailer.createTransport({ jsonTransport: true, disableFileAccess: true, disableUrlAccess: true });
  const jsonInfo = await sendMail(jsonTransport, {
    from: 'sender@example.test',
    to: 'recipient@example.test',
    subject: 'json file bypass',
    text: 'body',
    attachments: [{ filename: 'secret.txt', path: fixture }]
  });
  const jsonMessage = JSON.parse(jsonInfo.message);
  const decoded = Buffer.from(jsonMessage.attachments[0].content, 'base64').toString('utf8');
  console.log('JSON_FILE_BYPASS=' + (decoded === marker));
  console.log('JSON_FILE_CONTENT=' + decoded);

  const streamTransport = nodemailer.createTransport({ streamTransport: true, buffer: true, disableFileAccess: true });
  try {
    await sendMail(streamTransport, {
      from: 'sender@example.test',
      to: 'recipient@example.test',
      subject: 'stream control',
      text: 'body',
      attachments: [{ filename: 'secret.txt', path: fixture }]
    });
    console.log('STREAM_FILE_CONTROL=NO_ERROR');
  } catch (err) {
    console.log('STREAM_FILE_CONTROL=' + err.code);
  }

  const server = http.createServer((req, res) => {
    console.log('LOCAL_HTTP_REQUEST=' + req.method + ' ' + req.url);
    res.end('LOCAL_HTTP_MARKER');
  });
  await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
  const url = 'http://127.0.0.1:' + server.address().port + '/private';
  const jsonUrlInfo = await sendMail(jsonTransport, {
    from: 'sender@example.test',
    to: 'recipient@example.test',
    subject: 'json url bypass',
    text: { href: url }
  });
  const jsonUrlMessage = JSON.parse(jsonUrlInfo.message);
  console.log('JSON_URL_BYPASS=' + (jsonUrlMessage.text === 'LOCAL_HTTP_MARKER'));
  const streamUrlTransport = nodemailer.createTransport({ streamTransport: true, buffer: true, disableUrlAccess: true });
  try {
    await sendMail(streamUrlTransport, {
      from: 'sender@example.test',
      to: 'recipient@example.test',
      subject: 'stream url control',
      text: { href: url }
    });
    console.log('STREAM_URL_CONTROL=NO_ERROR');
  } catch (err) {
    console.log('STREAM_URL_CONTROL=' + err.code);
  }
  server.close();
  fs.unlinkSync(fixture);
})().catch(err => { try { fs.unlinkSync(fixture); } catch (E) {} console.error(err && err.stack || err); process.exit(1); });
NODE
```

Observed output in this environment:

```text
JSON_FILE_BYPASS=true
JSON_FILE_CONTENT=NM_JSON_BYPASS_1779802076150
STREAM_FILE_CONTROL=EFILEACCESS
LOCAL_HTTP_REQUEST=GET /private
JSON_URL_BYPASS=true
STREAM_URL_CONTROL=EURLACCESS
```

Expected vulnerable output: `JSON_FILE_BYPASS=true`, the printed temporary marker in `JSON_FILE_CONTENT`, a `LOCAL_HTTP_REQUEST=GET /private` line, and `JSON_URL_BYPASS=true`. Expected negative/control output: `STREAM_FILE_CONTROL=EFILEACCESS` and `STREAM_URL_CONTROL=EURLACCESS`, showing the same policy flags work in the normal streaming transport.

Cleanup: the PoC removes its temporary fixture file before exiting and closes the local HTTP server.

### Impact

If an application uses `jsonTransport` to safely serialize or queue partially user-controlled Nodemailer message objects while relying on `disableFileAccess` / `disableUrlAccess`, an attacker can bypass those protections. The file-read variant can copy local file contents into the generated JSON message output. The URL-fetch variant can force outbound HTTP requests from the application host to local or internal services despite URL access being disabled. The impact depends on what message fields the embedding application exposes and where it stores or returns the generated JSON, but the local PoC confirms both protected sink operations are reached.

### Suggested remediation

Enforce `disableFileAccess` and `disableUrlAccess` inside `shared.resolveContent()` or pass an explicit policy object into every pre-resolution call and reject protected `path` / `href` values before opening files or fetching URLs. Apply the same fix to `jsonTransport` normalization and the `attachDataUrls` pre-plugin path. Add regression tests showing `jsonTransport` returns `EFILEACCESS` / `EURLACCESS` for file and URL content when those flags are set, and that `attachDataUrls` cannot resolve object-form `html.path` / `html.href` when the corresponding access flag is disabled.

## References
- https://github.com/nodemailer/nodemailer/security/advisories/GHSA-wqvq-jvpq-h66f
- https://github.com/nodemailer/nodemailer
