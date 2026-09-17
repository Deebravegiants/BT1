# [M] CefSharp.Common: `FolderSchemeHandlerFactory` path boundary check can expose files outside the configured root folder

## Summary
Severity: Medium
Advisory: GHSA-85jm-cwp2-mvpv
CVE: CVE-2026-48796
CWE: CWE-22
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-06-30
Source: https://github.com/advisories/GHSA-85jm-cwp2-mvpv
Type: github-advisory

## Affected
- NuGet: `CefSharp.Common` — affected >=0 <148.0.90

## Details
### Summary

`FolderSchemeHandlerFactory` was intended to restrict served files to a configured `rootFolder`, but its path validation used a raw string prefix check. A request could escape to a sibling directory whose full path starts with the root folder path, allowing files outside the configured root to be served.

### Details

In affected versions, `FolderSchemeHandlerFactory` canonicalized `rootFolder`, decoded the request path, combined it with the root, and then allowed the file when:

```csharp
filePath.StartsWith(rootFolder, StringComparison.OrdinalIgnoreCase)
```

This does not enforce a directory boundary. For example, `/tmp/app/www2/secret.txt` starts with `/tmp/app/www`, but `www2` is a sibling of `www`, not a child. The same issue applies on Windows, for example `C:\app\www2\secret.txt` starts with `C:\app\www`.

The affected code was reviewed at commit `b5fef3bb4bc58798c95170078c41de92cfe9066e`, assembly version `147.0.100`.

### PoC

Set `rootFolder` to a directory named `www` and create a sibling directory named `www2`:

```text
<temp>/www/index.html
<temp>/www2/secret.txt
```

Register `FolderSchemeHandlerFactory` for `<temp>/www`, then request:

```text
https://folderschemehandlerfactory.test/..%2fwww2/secret.txt
```

The request path is URL-decoded to `../www2/secret.txt`, combined with `<temp>/www`, and canonicalized to:

```text
<temp>/www2/secret.txt
```

Because `<temp>/www2/secret.txt` starts with `<temp>/www` as a string prefix, the affected check passes and `secret.txt` is served from outside `rootFolder`.

Expected vulnerable result: HTTP 200 with the contents of `<temp>/www2/secret.txt`.

Expected fixed result: 404 or equivalent not-found response because the resolved file is outside `rootFolder`.

### Impact

Applications using `FolderSchemeHandlerFactory` for a custom scheme or registered HTTP/HTTPS scheme may expose local files outside the intended served directory. This is most relevant when sensitive sibling directories share the root path prefix, such as `www`/`www2`, `public`/`public_backup`, or `static`/`static-secrets`.

An attacker must be able to cause the embedded browser to request URLs handled by the affected scheme registration.

## References
- https://github.com/cefsharp/CefSharp/security/advisories/GHSA-85jm-cwp2-mvpv
- https://github.com/cefsharp/CefSharp
