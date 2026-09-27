# [M] ImageMagick has Undefined Behavior (function-type-mismatch) in CloneSplayTree

## Summary
Severity: Medium
Advisory: GHSA-6hgw-6x87-578x
CVE: CVE-2025-55160
CWE: CWE-758
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:L (CVSS_V3)
Published: 2025-08-25
Source: https://github.com/advisories/GHSA-6hgw-6x87-578x
Type: github-advisory

## Affected
- NuGet: `Magick.NET-Q16-AnyCPU` — affected >=0 <14.8.0
- NuGet: `Magick.NET-Q16-HDRI-AnyCPU` — affected >=0 <14.8.0
- NuGet: `Magick.NET-Q16-HDRI-OpenMP-arm64` — affected >=0 <14.8.0
- NuGet: `Magick.NET-Q16-HDRI-OpenMP-x64` — affected >=0 <14.8.0
- NuGet: `Magick.NET-Q16-HDRI-arm64` — affected >=0 <14.8.0
- NuGet: `Magick.NET-Q16-HDRI-x64` — affected >=0 <14.8.0
- NuGet: `Magick.NET-Q16-HDRI-x86` — affected >=0 <14.8.0
- NuGet: `Magick.NET-Q16-OpenMP-arm64` — affected >=0 <14.8.0
- NuGet: `Magick.NET-Q16-OpenMP-x64` — affected >=0 <14.8.0
- NuGet: `Magick.NET-Q16-arm64` — affected >=0 <14.8.0
- NuGet: `Magick.NET-Q16-x64` — affected >=0 <14.8.0
- NuGet: `Magick.NET-Q16-x86` — affected >=0 <14.8.0
- NuGet: `Magick.NET-Q8-AnyCPU` — affected >=0 <14.8.0
- NuGet: `Magick.NET-Q8-OpenMP-arm64` — affected >=0 <14.8.0
- NuGet: `Magick.NET-Q8-OpenMP-x64` — affected >=0 <14.8.0
- NuGet: `Magick.NET-Q8-arm64` — affected >=0 <14.8.0
- NuGet: `Magick.NET-Q8-x64` — affected >=0 <14.8.0
- NuGet: `Magick.NET-Q8-x86` — affected >=0 <14.8.0

## Details
## Summary
- **Target:** ImageMagick (commit `ecc9a5eb456747374bae8e07038ba10b3d8821b3`)
- **Type:** Undefined Behavior (function-type-mismatch) in splay tree cloning callback
- **Impact:** Deterministic abort under UBSan (DoS in sanitizer builds). No crash in a non-sanitized build; likely low security impact.
- **Trigger:** Minimal **2-byte** input parsed via MagickWand, then coalescing.
## Environment
OS: macOS (Apple Silicon/arm64)
Homebrew clang version 20.1.8
Target: arm64-apple-darwin24.5.0
Thread model: posix
InstalledDir: /opt/homebrew/Cellar/llvm/20.1.8/bin
Configuration file: /opt/homebrew/etc/clang/arm64-apple-darwin24.cfg
Homebrew ImageMagick: `magick -version` → `ImageMagick 7.1.2-0 Q16-HDRI aarch64`
pkg-config: `MagickWand-7.Q16HDRI` version `7.1.2`
Library configure flags (capsule build):
./configure --disable-shared --enable-static --without-modules --without-magick-plus-plus --disable-openmp --without-perl --without-x --with-png=yes --without-jpeg --without-tiff --without-xml --without-lqr --without-gslib
Harness compile flags:
-fsanitize=fuzzer,address,undefined -fno-omit-frame-pointer
pkg-config cflags/libs supplied:
-I<...>/include/ImageMagick-7
-DMAGICKCORE_HDRI_ENABLE=1 -DMAGICKCORE_QUANTUM_DEPTH=16 -DMAGICKCORE_CHANNEL_MASK_DEPTH=32
and linked against MagickWand-7.Q16HDRI and MagickCore-7.Q16HDRI
Sanitizer runtime:
ASan+UBSan defaults. Repro also with `UBSAN_OPTIONS=print_stacktrace=1:halt_on_error=1`
## PoC
- **Bytes (hex):** `1c 02`
- **Base64:** `HAI=`
 - **sha256 (optional):** <fill in>
## Reproduction
Create PoC:

`printf '\x1c\x02' > poc.bin`

Option A: libFuzzer harness
- Run once: `./harness_ImageMagick_... -runs=1 ./poc.bin`
- Expected: UBSan aborts with function-type-mismatch at `MagickCore/splay-tree.c:372:43`.

Option B: standalone reproducer (C)
- Compile (ensure `PKG_CONFIG_PATH` points to your ImageMagick if needed):

/opt/homebrew/opt/llvm/bin/clang -g -O1 -fsanitize=address,undefined $(/opt/homebrew/bin/pkg-config --cflags MagickWand-7.Q16HDRI) repro.c -o repro $(/opt/homebrew/bin/pkg-config --libs MagickWand-7.Q16HDRI)

- Run:

UBSAN_OPTIONS=print_stacktrace=1:halt_on_error=1 ./repro ./poc.bin
Observed output (excerpt)
MagickCore/splay-tree.c:372:43: runtime error: call to function ConstantString through pointer to incorrect function type 'void *(*)(void *)'
string.c:680: note: ConstantString defined here
#0 CloneSplayTree splay-tree.c:372
#1 CloneImageProfiles profile.c:159
#2 CloneImage image.c:832
#3 CoalesceImages layer.c:269
#4 MagickCoalesceImages magick-image.c:1665
#5 main repro.c:XX
Root cause
The splay tree clone callback expects a function pointer of type `void *(*)(void *)`. ConstantString has a different signature (`char *ConstantString(const char *)`). Calling through the mismatched function type is undefined behavior in C and triggers UBSan’s function-type-mismatch.
The path is exercised during coalescing: CloneImage → CloneImageProfiles → CloneSplayTree.
Scope
Reproduces with a minimal, sanitizer-instrumented, PNG-enabled build and delegates disabled (policy.xml), suggesting the issue is in MagickCore rather than external delegates.
Suggested fix (sketch)
Use a wrapper that matches the expected callback prototype, or adjust the splay-tree callback typedef for const-correctness. For example:
static void *CloneStringShim(const void *p) {
return (void *) ConstantString((const char *) p);
}

/* When setting splay-tree clone_value, use CloneStringShim instead of ConstantString. */

Alternatively, update the clone callback typedefs to use const void* consistently (and return void*) and ensure callers pass a correctly typed wrapper.

Artifacts
Minimised PoC: attached (poc.bin, 2 bytes; base64 HAI=)
Harness source and exact build command (attached)
Full UBSan trace (attached)
Commit SHA and configure flags (above)
Credits
Discovered by: Lumina Mescuwa
Method: libFuzzer + UBSan
Verification
- UBSan build: Reproduces with `halt_on_error=1`; aborts at `MagickCore/splay-tree.c:372`.
- Non-sanitized Homebrew build (macOS arm64, clang 20.1.8): No crash; repro completes silently.

## References
- https://github.com/ImageMagick/ImageMagick/security/advisories/GHSA-6hgw-6x87-578x
- https://nvd.nist.gov/vuln/detail/CVE-2025-55160
- https://github.com/ImageMagick/ImageMagick
- https://github.com/dlemstra/Magick.NET/releases/tag/14.8.0
