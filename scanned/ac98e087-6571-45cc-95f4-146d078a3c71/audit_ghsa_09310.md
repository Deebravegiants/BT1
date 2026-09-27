# [M] kanidmd_lib: Image upload validators run before authorization; PNG validator panics on malformed input

## Summary
Severity: Medium
Advisory: GHSA-84jc-3hj2-hwc7
CWE: CWE-190, CWE-20, CWE-696
Ecosystem: crates.io
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:L/SC:N/SI:N/SA:L (CVSS_V4)
Published: 2026-05-06
Source: https://github.com/advisories/GHSA-84jc-3hj2-hwc7
Type: github-advisory

## Affected
- crates.io: `kanidmd_lib` — affected >=0 <1.9.3

## Details
### Summary
The `POST /v1/domain/_image` and `POST /v1/oauth2/{rs_name}/_image` handlers call `validate_image()` on the uploaded body **before** the ACL check that restricts image upload to admins. Any bug in an image validator is therefore reachable by an unauthenticated remote client rather than being admin-gated.

One such bug exists today: `png_has_trailer()` panics on inputs shorter than 8 bytes, or whose first chunk-length field is near `u32::MAX`.

**On a default build this has no server-wide impact.** The panic unwinds only the requester's own tokio task; the server process survives, no shared state is poisoned, and other connections are unaffected. This was reported privately rather than as a public issue because (a) the project previously treated an admin-triggered thread crash of identical impact as security-relevant (e51d0dee4), and this is reachable by a broader population; and (b) a downstream build with `panic = "abort"` would upgrade it to an unauthenticated process-crash DoS.

### Details

#### Validate-before-authorize ordering

Both handlers parse and validate attacker-controlled bytes before checking whether the caller is permitted to upload at all:

- `server/core/src/https/v1_domain.rs:118` — `image.validate_image()` runs; `handle_image_update(client_auth_info, …)` (the ACL check) is at line 129.
- `server/core/src/https/v1_oauth2.rs:550` — same ordering.

The `VerifiedClientInformation` extractor (`server/core/src/https/extractors/mod.rs:18-90`) always returns `Ok` — it builds a `ClientAuthInfo` from whatever credentials are present (including none) and does not reject anonymous callers. Authorization is deferred to `handle_image_update()`, which is never reached if the validator panics or errors first.

#### PNG validator panic (demonstrator)

`validate_image()` (`server/lib/src/valueset/image/mod.rs:98`) checks only a 256 KiB maximum size, not a minimum, before dispatching to the format-specific validator.

**Short input** — `server/lib/src/valueset/image/png.rs:73-76`:

```rust
pub fn png_has_trailer(contents: &Vec<u8>) -> Result<bool, ImageValidationError> {
    let buf = contents.as_slice();
    let (magic, buf) = buf.split_at(PNG_PRELUDE.len()); // 8; panics if len < 8
```

**Chunk-length overflow** — `server/lib/src/valueset/image/png.rs:46,53`:

```rust
if buf.len() < (length + 4) as usize {   // length: u32; wraps before the usize cast
    ...
}
let (_, buf) = buf.split_at(length as usize);   // panics for length ≈ u32::MAX
```

In a release build `0xFFFF_FFFC + 4` wraps to `0`, the guard passes, and `split_at` panics.

### PoC

```sh
printf '\x89PNG' > /tmp/short.png
curl -sk https://$KANIDM_HOST/v1/domain/_image \
     -F 'image=@/tmp/short.png;type=image/png;filename=x.png'
# → connection reset / empty reply; server process remains up
```

Unit-test confirmation (`cargo test -p kanidmd_lib --lib`):

```rust
#[test]
fn audit_png_short_input_panics() {
    let short = vec![0x89u8, 0x50, 0x4e, 0x47];
    assert!(std::panic::catch_unwind(|| png_has_trailer(&short)).is_err());
}

#[test]
fn audit_png_chunk_length_overflow_panics() {
    let mut data = vec![0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a];
    data.extend_from_slice(&[0xFF, 0xFF, 0xFF, 0xFD]);
    data.extend_from_slice(b"IHDR");
    data.extend_from_slice(&[0u8; 8]);
    assert!(std::panic::catch_unwind(|| png_has_trailer(&data)).is_err());
}
```

Both tests pass (i.e. both inputs panic).

### Impact

The only party affected is the requester, whose own connection is dropped. Repeating the request has no cumulative effect beyond ordinary request load.

On the upstream build:

- Each connection runs in its own `tokio::task::spawn` (`server/core/src/https/mod.rs:481`); the accept loop continues after a task panic.
- No `panic = "abort"` in any workspace `[profile.*]`.
- No `Mutex`/`RwLock` held across the call site; nothing is poisoned.
- The panic occurs before any write actor is messaged; no DB or replication state is touched.

**Residual risk:** a downstream packager that sets `panic = "abort"` (or links code that installs an abort handler) would see a full unauthenticated process crash. (No such packager is known)

**Affected:** v1.1.0-rc.15 (introduced in e7f594a1c, #2112) through `master` @ edf50b9da.

## References
- https://github.com/kanidm/kanidm/security/advisories/GHSA-84jc-3hj2-hwc7
- https://github.com/kanidm/kanidm
