# [H] scim_proto and kanidm_proto have an authenticated process abort via SCIM filter stack exhaustion

## Summary
Severity: High
Advisory: GHSA-r5fr-9gmv-jggh
CVE: CVE-2026-46689
CWE: CWE-248, CWE-400, CWE-674
Ecosystem: crates.io
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-05-06
Source: https://github.com/advisories/GHSA-r5fr-9gmv-jggh
Type: github-advisory

## Affected
- crates.io: `scim_proto` — affected >=0 <1.9.3
- crates.io: `kanidm_proto` — affected >=0 <1.9.3

## Details
### Summary

A single unauthenticated `GET` to any `/scim/v1/...` endpoint with a `?filter=` query string of a few thousand nested parentheses (≈ 4–12 KB) drives the recursive-descent PEG parser past the worker thread's stack guard page. Rust responds to stack overflow with `std::process::abort()` — the entire `kanidmd` process exits. The parse runs inside axum's `Query<ScimEntryGetQuery>` extractor, before any handler body and therefore before any ACL check.

### Details

The SCIM filter grammar recurses on `(` and `not (` with no depth bound.

**`proto/src/scim_v1/mod.rs:263-433`** — `peg::parser! { grammar scimfilter() ... }`:

```rust
// line 281
"not" separator()+ "(" e:parse() ")" { ScimFilter::Not(Box::new(e)) }
// line 293
"(" e:parse() ")" { e }
```

Both rules re-enter `parse()` without a depth counter.

**`proto/src/scim_v1/mod.rs:442-447`** — `impl FromStr for ScimFilter` calls `scimfilter::parse(input)` directly on the raw string with no length or depth pre-check.

**`proto/src/scim_v1/mod.rs:80-81`** — `ScimEntryGetQuery.filter` is `#[serde_as(as = "Option<DisplayFromStr>")]`, so deserialising the query struct invokes `ScimFilter::from_str` on attacker bytes.

**Unauthenticated reachability** — nine handlers in `server/core/src/https/v1_scim.rs` (route table at lines 865-1029) take `Query<ScimEntryGetQuery>` as an argument: `/scim/v1/Entry`, `/scim/v1/Entry/{id}`, `/scim/v1/Person/{id}`, `/scim/v1/Application`, `/scim/v1/Application/{id}`, `/scim/v1/Class`, `/scim/v1/Attribute`, `/scim/v1/Message`, `/scim/v1/Message/{id}`. The SCIM router is merged unconditionally for every server role (`server/core/src/https/mod.rs:312`).

Axum extracts handler arguments before the handler body runs. The preceding `VerifiedClientInformation` extractor (`server/core/src/https/extractors/mod.rs:16-91`) always returns `Ok` (line 89) regardless of credentials; authorization is deferred to the handler body, which is never reached.

The existing semantic depth limit (`DEFAULT_LIMIT_FILTER_DEPTH_MAX = 12`, `server/lib/src/constants/mod.rs:212`) is enforced in `Filter::from_scim_ro` (`server/lib/src/filter.rs:786`) **after** the PEG parse has already produced an AST, so it cannot prevent the parser itself from blowing the stack.

The production daemon (`server/daemon/src/main.rs:735-744`) uses `new_multi_thread()` with default 2 MiB worker stacks; hyper's `max_buf_size` (~400 KiB) is not lowered (`server/core/src/https/mod.rs:708-727`), so a 12 KB URI is accepted.

An identical unbounded grammar exists in `libs/scim_proto/src/filter.rs:112-276` (not network-reachable, but should be fixed in the same patch).

### PoC

```sh
curl -sk "https://idm.example.com/scim/v1/Application?filter=$(python3 -c 'print("("*3000+"a+pr"+")"*3000)')"
# → curl: (52) Empty reply from server
# → server journal: "fatal runtime error: stack overflow, aborting", SIGABRT
```

Release-build threshold measured at ~2 000 nesting levels / ~4 KB:

```
$ cargo test --release -p kanidm_proto --test scim_filter_depth -- --nocapture
parens depth=1500 len=3004
  -> survived
parens depth=2000 len=4004

thread 'audit_scim_filter_nested_parens' has overflowed its stack
fatal runtime error: stack overflow, aborting
  (signal: 6, SIGABRT: process abort signal)
```

End-to-end against an in-process server via `kanidmd_testkit` (no authentication performed):

```
Testkit server setup complete - http://localhost:18080/
audit_scim_dos: sending unauthenticated GET, url len = 12056

thread '...' has overflowed its stack
fatal runtime error: stack overflow, aborting
  (signal: 6, SIGABRT: process abort signal)
```

### Impact

Process-wide availability loss; no confidentiality or integrity impact.

- **Unauthenticated**, default install, no feature flag required.
- **Process abort, not task panic.** Stack overflow triggers libstd's guard-page handler, which calls `std::process::abort()`. tokio's per-task `catch_unwind` isolation does not apply to aborts. All in-flight HTTP requests, OAuth2/OIDC sessions, LDAP binds, and the web UI are terminated.
- **Repeatable.** One ~12 KB GET per crash; a `while true; do curl ...; done` loop holds the service down indefinitely across supervisor restarts.
- The 6 011-byte variant (`depth=3000`) fits under the nginx default `large_client_header_buffers` limit of 8 KB, so a typical reverse proxy does not mitigate.

**Affected**: v1.7.0 through `master` @ edf50b9da.

## References
- https://github.com/kanidm/kanidm/security/advisories/GHSA-r5fr-9gmv-jggh
- https://nvd.nist.gov/vuln/detail/CVE-2026-46689
- https://github.com/kanidm/kanidm
- https://github.com/kanidm/kanidm/releases/tag/v1.9.3
