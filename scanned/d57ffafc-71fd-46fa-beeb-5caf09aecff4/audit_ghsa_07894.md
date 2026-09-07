# [H] AdonisJS vulnerable to Denial of Service (DoS) via Unrestricted Memory Buffering in PartHandler during File Type Detection

## Summary
Severity: High
Advisory: GHSA-xx9g-fh25-4q64
CVE: CVE-2026-25762
CWE: CWE-400, CWE-770
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-02-06
Source: https://github.com/advisories/GHSA-xx9g-fh25-4q64
Type: github-advisory

## Affected
- npm: `@adonisjs/bodyparser` — affected >=0 <10.1.3
- npm: `@adonisjs/bodyparser` — affected >=11.0.0-next.0 <11.0.0-next.9

## Details
### Summary

A Denial of Service (DoS) vulnerability (CWE-400) exists in the multipart file handling logic of `@adonisjs/bodyparser`. When processing file uploads, the multipart parser may accumulate an unbounded amount of data in memory while attempting to detect file types, potentially leading to excessive memory consumption and process termination.

This issue affects applications that accept `multipart/form-data` uploads using affected versions of `@adonisjs/bodyparser`.

### Details

AdonisJS parses `multipart/form-data` requests using the BodyParser package. During file uploads, the multipart parser attempts to detect the uploaded file type by accumulating incoming chunks in an internal buffer to perform magic number detection.

The internal buffer used for this detection does not enforce a maximum size and is not protected by a timeout or early termination condition. If the uploaded data does not match any supported file signatures, the buffer continues to grow as more chunks are received.

When certain configurations are used, such as deferred validations or permissive file size limits, this buffering behavior may persist for the duration of the upload stream.

### Impact

Exploitation requires a reachable endpoint that accepts multipart file uploads.

An attacker can send a specially crafted multipart request containing a large or unbounded stream of data that does not match known file signatures. This may cause the server to continuously allocate memory until the Node.js process exhausts available RAM and terminates due to an out-of-memory condition.

This results in a Denial of Service, making the application unavailable to legitimate users. Authentication is not required if the upload endpoint is publicly accessible.

### Patches

Fixes targeting v6 and v7 have been published below.

Users should upgrade to a version that includes the following fix:
- https://github.com/adonisjs/bodyparser/releases/tag/v10.1.3
- https://github.com/adonisjs/bodyparser/releases/tag/v11.0.0-next.9

## References
- https://github.com/adonisjs/core/security/advisories/GHSA-xx9g-fh25-4q64
- https://nvd.nist.gov/vuln/detail/CVE-2026-25762
- https://github.com/adonisjs/bodyparser/releases/tag/v10.1.3
- https://github.com/adonisjs/bodyparser/releases/tag/v11.0.0-next.9
- https://github.com/adonisjs/core
