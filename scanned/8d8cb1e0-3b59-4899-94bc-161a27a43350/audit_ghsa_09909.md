# [H] WWBN AVideo has an Allowlisted downloadURL media extensions bypass SSRF protection and enable internal response exfiltration (Incomplete fix for CVE-2026-27732)

## Summary
Severity: High
Advisory: GHSA-cmcr-q4jf-p6q9
CVE: CVE-2026-39370
CWE: CWE-918
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2026-04-08
Source: https://github.com/advisories/GHSA-cmcr-q4jf-p6q9
Type: github-advisory

## Affected
- Packagist: `WWBN/AVideo` — affected >=0

## Details
## Summary

The fix for [CVE-2026-27732](https://github.com/WWBN/AVideo/security/advisories/GHSA-h39h-7cvg-q7j6) is incomplete.

`objects/aVideoEncoder.json.php` still allows attacker-controlled `downloadURL` values with common media or archive extensions such as `.mp4`, `.mp3`, `.zip`, `.jpg`, `.png`, `.gif`, and `.webm` to bypass SSRF validation. The server then fetches the response and stores it as media content.

This allows an authenticated uploader to turn the upload-by-URL flow into a reliable SSRF response-exfiltration primitive.

## Details

`objects/aVideoEncoder.json.php` accepts attacker-controlled `downloadURL` and passes it to `downloadVideoFromDownloadURL()`.

Inside that function:

1. the URL extension is extracted from the attacker-controlled path
2. the extension is checked against an allowlist of normal encoder formats
3. `isSSRFSafeURL()` is skipped for common media and archive extensions
4. the URL is fetched via `url_get_contents()`
5. the fetched body is written into video storage and exposed through normal media metadata

The current code still contains:

- an extension-based bypass for SSRF validation
- no mandatory initial-destination SSRF enforcement inside `url_get_contents()` itself

This means internal URLs such as:

`http://127.0.0.1:9998/probe.mp4`

remain reachable from the application host.

This issue is best described as an incomplete fix / patch bypass of `CVE-2026-27732`, not a separate unrelated SSRF class.

## Proof of concept

1. Log in as a low-privilege uploader.
2. Start an HTTP service reachable only from inside the application environment, for example:

```text
http://127.0.0.1:9998/probe.mp4
```

3. Confirm that the service is not reachable externally.
4. Send:

```text
POST /objects/aVideoEncoder.json.php
downloadURL=http://127.0.0.1:9998/probe.mp4
format=mp4
```

5. If needed, replay once against the returned `videos_id` with `first_request=1` so the fetched bytes land in the normal media path.
6. Query:

```text
GET /objects/videos.json.php?showAll=1
```

7. Recover `videosURL.mp4.url`.
8. Download that media URL and observe that the body matches the internal-only response byte-for-byte.

## Impact

An authenticated uploader can make the AVideo server fetch loopback or internal HTTP resources and persist the response as media content by supplying a `downloadURL` ending in an allowlisted extension such as `.mp4`, `.jpg`, `.gif`, or `.zip`. Because SSRF validation is skipped for those extensions, the fetched body is stored and later retrievable through the generated `/videos/...` media URL. Successful exploitation allows internal response exfiltration from private APIs, admin endpoints, or other internal services reachable from the application host.


## Recommended fix

- Apply `isSSRFSafeURL()` to all `downloadURL` inputs regardless of extension
- Remove extension-based exceptions from SSRF enforcement
- Move initial-destination SSRF validation into `url_get_contents()` so call sites cannot skip it
- Avoid storing arbitrary fetched content directly as publicly retrievable media
- Consider restricting upload-by-URL to an explicit allowlist of trusted fetch origins

## References
- https://github.com/WWBN/AVideo/security/advisories/GHSA-cmcr-q4jf-p6q9
- https://nvd.nist.gov/vuln/detail/CVE-2026-39370
- https://github.com/WWBN/AVideo
