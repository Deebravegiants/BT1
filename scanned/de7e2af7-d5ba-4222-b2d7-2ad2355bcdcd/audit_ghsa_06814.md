# [H] Thumbor has HMAC validation bypass via multiple .replace() calls when removing URL signature

## Summary
Severity: High
Advisory: GHSA-mw3h-qjxj-6xg9
CVE: CVE-2026-53501
CWE: CWE-347
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:L (CVSS_V3)
Published: 2026-07-31
Source: https://github.com/advisories/GHSA-mw3h-qjxj-6xg9
Type: github-advisory

## Affected
- PyPI: `thumbor` — affected >=0 <7.8.0

## Details
# HMAC validation bypass via multiple `.replace()` calls when removing URL signature

## Summary

Thumbor’s HMAC validation can be bypassed due to the use of Python’s `.replace()` when removing the signature from the URL before validation. Since `.replace()` removes **all occurrences** of the substring, an attacker can insert the same signature multiple times in the URL and manipulate the final URL used for validation.

This allows crafting URLs where the validated string differs from the actual requested resource, enabling loading images from unintended domains or paths.

## Details

Thumbor signs URLs using **HMAC-SHA1** to prevent abuse such as loading arbitrary external images or invoking filters without authorization.

During request validation, Thumbor removes the signature from the request URL before recalculating the HMAC. The relevant code:

```python
url_signature = self.context.request.hash
if url_signature:
    signer = self.context.modules.url_signer(
        self.context.server.security_key
    )

    try:
        quoted_hash = quote(self.context.request.hash)
    except KeyError:
        self._error(400, f"Invalid hash: {self.context.request.hash}")
        return

    url_to_validate = url.replace(
        f"/{self.context.request.hash}/", ""
    ).replace(f"/{quoted_hash}/", "")

    valid = signer.validate(
        unquote(url_signature).encode(), url_to_validate
    )
```

The issue is that `.replace()` removes **every occurrence** of the substring in the URL, not just the first one.

Because the signature itself appears in the URL, an attacker can **inject additional copies of the signature** elsewhere in the path. When Thumbor performs `.replace()`, these extra occurrences are also removed, resulting in a different `url_to_validate` than the original request.

## Example

Valid request:

```
/ddoyYVYUbDf6Po_dzOrBhCDrXLc=/300x200/s3.glbimg.com/v1/.../image.jpg
```

By injecting the same hash inside the URL:

```
/ddoyYVYUbDf6Po_dzOrBhCDrXLc=/300x200/s3.glbimg.co/ddoyYVYUbDf6Po_dzOrBhCDrXLc=/m/v1/.../image.jpg
```

After `.replace()` removes all occurrences of the hash, the URL used for validation differs from the effective request path. This allows manipulation of the upstream host or path.

Further manipulation is possible due to the **second `.replace()` for the URL-encoded hash (`%3D`)**, enabling more precise path manipulation.

Example:

```
/ddoyYVYUbDf6Po_dzOrBhCDrXLc=/300x200/s3.glbimg.com/ddoyYVYUbDf6Po/ddoyYVYUbDf6Po_dzOrBhCDrXLc%3D/ddoyYVYUbDf6Po/v1/...
```

## Impact

This behavior may allow attackers to:

- Bypass HMAC URL validation
- Load images from arbitrary domains
- Abuse Thumbor deployments as an open proxy / image fetcher
- Circumvent domain restrictions intended by the signed URL mechanism

## Root Cause

Use of `.replace()` without limiting the number of replacements when removing the signature from the URL.

Since the signature is part of the request path, using a global replacement allows attackers to place additional occurrences of the same substring to influence the validated string.

## Suggested Fix

Remove only the first occurrence of the signature or explicitly parse the URL components instead of performing global string replacement.

Example:

```python
url.replace(f"/{self.context.request.hash}/", "", 1)
```

Alternatively, reconstruct the unsigned URL deterministically from the parsed request components.

## References
- https://github.com/thumbor/thumbor/security/advisories/GHSA-mw3h-qjxj-6xg9
- https://github.com/thumbor/thumbor/commit/e3ae3e2500537b4d735df4144129a649374bb70b
- https://github.com/thumbor/thumbor
- https://github.com/thumbor/thumbor/releases/tag/7.8.0
