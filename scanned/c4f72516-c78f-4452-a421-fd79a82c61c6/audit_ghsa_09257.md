# [M] oxidize-pdf: NaN/inf bypass in colour content-stream emission causes PDF rejection (DoS)

## Summary
Severity: Medium
Advisory: GHSA-88q9-cmp2-c2vq
CWE: CWE-1284, CWE-20
Ecosystem: NuGet, PyPI, crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2026-05-11
Source: https://github.com/advisories/GHSA-88q9-cmp2-c2vq
Type: github-advisory

## Affected
- crates.io: `oxidize-pdf` — affected >=0 <2.6.0
- NuGet: `OxidizePdf.NET` — affected >=0 <0.8.0
- PyPI: `oxidize-pdf` — affected >=0 <0.5.0

## Details
### Impact

  `oxidize-pdf` defines `Color` as a `pub enum` with public tuple-struct variants `Rgb(f64, f64, f64)`, `Gray(f64)`, and `Cmyk(f64, f64, f64, f64)`. The constructors `Color::rgb`, `Color::gray`, and `Color::cmyk` clamp incoming
  components to `[0.0, 1.0]`, but because the variants are `pub`, callers can construct values directly without going through the constructors:

  ```rust
  let safe   = Color::rgb(f64::NAN, 0.5, 0.5);   // clamps NaN to 0.0
  let attack = Color::Rgb(f64::NAN, 0.5, 0.5);    // bypasses clamp

  Color: Copy allows the non-finite value to propagate freely through API surfaces and serialisation. When such a value reaches a content-stream emitter, the writer formats it via format!("{:.3}", v). The Rust standard library renders
  f64::NAN as "NaN", f64::INFINITY as "inf", and f64::NEG_INFINITY as "-inf" — none of which are valid PDF numeric tokens per ISO 32000-1 §7.3.3:

  ▎ A numeric object shall be represented by one or more decimal digits with an optional sign and a leading, trailing, or embedded PERIOD.

  The resulting content stream contains an invalid token sequence (e.g. NaN 0.500 0.500 rg). Conformant PDF viewers (Adobe Acrobat, Foxit, PDF.js, Apple Preview) reject the content stream, the affected page, or the entire document
  depending on parser strictness.

  Affected packages (all listed in the "Affected products" section of this advisory):

  - oxidize-pdf on crates.io — the core Rust library where the vulnerable code path lives.
  - OxidizePdf.NET on NuGet — .NET FFI binding that exposes Color through its public API; inherits the vulnerability from its dependency on oxidize-pdf.
  - oxidize-pdf on PyPI — Python bindings (PyO3) that similarly expose colour construction; inherits the vulnerability from its dependency.

  Who is impacted: any application that uses these packages to generate PDFs and accepts user-influenced colour values without validation. The most exposed surfaces are server-side PDF generators that take arbitrary f64 colour
  parameters from upstream services.

  Reproduction (Rust API):
  use oxidize_pdf::{Document, Page, graphics::Color};

  let mut doc = Document::new();
  let mut page = Page::a4();
  let gc = page.graphics();
  gc.set_fill_color(Color::Rgb(f64::NAN, 0.5, 0.5));
  gc.rectangle(50.0, 50.0, 100.0, 100.0).fill();
  doc.add_page(page);
  doc.save("malformed.pdf").unwrap();

  // The resulting content stream contains:
  //   NaN 0.500 0.500 rg
  //   50 50 100 100 re
  //   f
  // which conformant viewers reject.

  Affected sites in oxidize-pdf 2.5.7 (the same code paths are reached by both .NET and Python bindings via FFI):

  - oxidize-pdf-core/src/text/flow.rs (TextFlowContext)
  - oxidize-pdf-core/src/text/mod.rs (TextContext::apply_text_state_parameters)
  - oxidize-pdf-core/src/graphics/mod.rs (GraphicsContext::apply_fill_color / apply_stroke_color)
  - oxidize-pdf-core/src/graphics/patterns.rs (create_checkerboard_pattern / create_stripe_pattern / create_dots_pattern)
  - ~45 sibling sites across forms/*, annotations/*, layout/rich_text.rs, and writer/pdf_writer/mod.rs that emit colour through the same code path.

  Patches

  The fix introduces a sanitising helper at the emission boundary in graphics/color.rs:

  pub(crate) fn finite_or_zero(val: f64) -> f64 {
      if val.is_finite() { val } else { 0.0 }
  }

  Every colour-operator emitter (~50 sites across 17 files) now routes through fill_color_op / stroke_color_op / write_fill_color / write_stroke_color, which apply finite_or_zero before formatting. Non-finite components are substituted
  with 0.0, so the wire format remains ISO 32000-1 conformant regardless of the input.

  Patched releases:

  - oxidize-pdf 2.6.0 on crates.io — contains the fix at the source.
  - OxidizePdf.NET on NuGet — bumped to depend on oxidize-pdf 2.6.0 (see "Patched versions" above).
  - oxidize-pdf on PyPI — bumped to depend on oxidize-pdf 2.6.0 (see "Patched versions" above).

  Users should upgrade to the patched version of whichever package(s) they consume.

  Workarounds

  For users who cannot upgrade immediately:

  - Always construct colours via the safe constructors Color::rgb(), Color::gray(), Color::cmyk(), which clamp components to [0.0, 1.0] (no NaN/inf survives clamping).
  - Never use direct enum construction (Color::Rgb(...), Color::Gray(...), Color::Cmyk(...)) when components originate from untrusted input. The same applies to the corresponding APIs in the .NET and Python bindings.
  - Validate untrusted f64 colour inputs with f64::is_finite() (Rust) or equivalent checks (!double.IsFinite(v) in .NET, math.isfinite(v) in Python) before passing them to any oxidize-pdf API.

  These mitigations are partial — they cover the application layer but not other code paths that may construct Color values internally. The full fix is the upgrade to the patched versions.

  References

  - Issue: https://github.com/bzsanti/oxidizePdf/issues/220
  - Companion refactor: https://github.com/bzsanti/oxidizePdf/issues/221
  - Fix PR: https://github.com/bzsanti/oxidizePdf/pull/225
  - Release PR (oxidize-pdf 2.6.0): https://github.com/bzsanti/oxidizePdf/pull/226
  - .NET binding repository: https://github.com/bzsanti/oxidize-pdf-dotnet
  - Python binding repository: https://github.com/bzsanti/oxidize-python
  - ISO 32000-1 §7.3.3 (Numeric Objects): https://www.iso.org/standard/51502.html

  A broader follow-up tracks the same CWE class in non-colour numeric content-stream emitters (line widths, transformation matrices, dash arrays, text positioning, path operators) — to be addressed in oxidize-pdf 2.7.0 with its own
  advisory.

## References
- https://github.com/bzsanti/oxidizePdf/security/advisories/GHSA-88q9-cmp2-c2vq
- https://github.com/bzsanti/oxidizePdf
