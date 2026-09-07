# [M] ApostropheCMS: Arbitrary file read via import-export attachment-name path traversal

## Summary
Severity: Medium
Advisory: GHSA-79qf-vqgc-7xx3
CVE: CVE-2026-63667
CWE: CWE-22
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-09-02
Source: https://github.com/advisories/GHSA-79qf-vqgc-7xx3
Type: github-advisory

## Affected
- npm: `@apostrophecms/import-export` — affected >=0 <3.6.2

## Details
## Summary

The `@apostrophecms/import-export` module reconstructs the on-disk source path of every imported attachment from JSON metadata contained in the uploaded archive.

The archive carries an `aposAttachments.json` file whose `name` and `extension` fields are concatenated into a filesystem path with no traversal check. The zip-slip guard that the module applies during tar extraction validates tar entry names only and does not cover this second path, which is built after extraction.

The file at the resulting path is read and copied into the public uploads directory, then served over HTTP without authentication. A `../` sequence in `name` makes the module read a file outside the extraction directory and publish it at an anonymous URL.

Result: an authenticated contributor reads any file on the host whose name ends in an allowlisted extension (other users' uploaded documents, text or CSV dumps, PDFs) by importing a crafted archive and fetching the planted attachment anonymously.

## Affected

apostrophecms/apostrophe with the `@apostrophecms/import-export` module installed and registered. Module version 3.6.1 (current latest), tested against Apostrophe 4.31.0 (monorepo HEAD 4d478d9). Requires an account with the contributor role or higher; guest and anonymous requests are rejected. The module is not part of the default starter kit, so sites that never installed it are not affected. Files whose real name lacks an accepted file-group extension are not reachable.

## Root cause

The import parser builds each attachment's source path by concatenating attacker-controlled JSON fields: `lib/formats/gzip.js:46` sets `file.path = path.join(attachmentFilesPath, ${attachment._id}-${attachment.name}.${attachment.extension})` from the `aposAttachments.json` entries in the uploaded archive. That path flows unchanged through `lib/methods/import.js:832` (`insertAttachments`) into `lib/methods/import.js:1074` (`attachment.insert`), where uploadfs copies the referenced file into the public uploads directory served by `express.static`. The archive's only traversal guard, `lib/formats/gzip.js:143` (`if (name.includes('../'))`), validates tar entry names during extraction and never inspects the `name`/`extension` values used to construct the read path, so a `name` of `../../../../../../tmp/secret` escapes `attachmentFilesPath`. Reaching the sink requires only an authenticated session (`lib/methods/import.js:71`), view permission on the target type (`lib/methods/index.js:54`), and the `upload-attachment` permission enforced at `modules/@apostrophecms/attachment/index.js:442`, which the built-in contributor role holds. The trailing `.${extension}` is appended and checked against the file-group allowlist in `modules/@apostrophecms/attachment/index.js` (`getFileGroup`), so the target file's real name must end in an accepted extension (txt, csv, pdf, xls, doc, svg, and similar).

## Reproduction

Apostrophe 4.31.0 starter-kit-essentials, MongoDB, default roles, `@apostrophecms/import-export` 3.6.1 installed, local uploadfs backend.

1. Place a secret file outside the upload tree with an allowlisted extension.

```
$ cat /tmp/apos_victim_secret.txt
TOP-SECRET DB DUMP
DB_PASSWORD=Pr0d-Secret-9981
API_KEY=sk_live_victim_abcdef
```

2. Build a gzip archive whose `aposAttachments.json` points the attachment `name` at that file through traversal (`aposDocs.json` is `[]`).

```
[{"_id":"evilatt0001","name":"../../../../../../../../../../../../tmp/apos_victim_secret","extension":"txt","title":"loot","docIds":[],"crops":[]}]
```

3. As a contributor, import the archive through the module's import action (`POST /api/v1/@apostrophecms/<type>/import-export-import`), then fetch the created attachment with no session.

```
$ curl -i http://localhost:3500/uploads/attachments/evilatt0001-apos-victim-secret.txt
HTTP/1.1 200 OK
Content-Type: text/plain; charset=UTF-8

TOP-SECRET DB DUMP
DB_PASSWORD=Pr0d-Secret-9981
API_KEY=sk_live_victim_abcdef
```

Live-verified: a contributor-driven import reads `/tmp/apos_victim_secret.txt` (outside the extraction directory) and serves it at an anonymous URL; the same import run as a guest is rejected at the `upload-attachment` check (`modules/@apostrophecms/attachment/index.js:442`).

## Impact

- Read of arbitrary host files whose real name ends in an allowlisted extension (txt, csv, pdf, xls, doc, svg, and similar).
- Disclosure of other users' uploaded documents and any allowlisted-extension file readable by the Node process.
- The exfiltration target is copied to a public, unauthenticated URL.
- Triggered by the contributor role in a single import, no admin interaction.

## Credit

Jan Kahmen, [turingpoint](https://www.turingpoint.de) (jan@turingpoint.de)

## References
- https://github.com/apostrophecms/apostrophe/security/advisories/GHSA-79qf-vqgc-7xx3
- https://nvd.nist.gov/vuln/detail/CVE-2026-63667
- https://github.com/apostrophecms/apostrophe/commit/87cccf44a23d09420875ca8a3765eb3db843836a
- https://github.com/apostrophecms/apostrophe
