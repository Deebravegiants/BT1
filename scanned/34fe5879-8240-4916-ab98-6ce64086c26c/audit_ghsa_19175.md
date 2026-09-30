# [M] rust-openssl ssl::select_next_proto use after free

## Summary
Severity: Medium
Advisory: GHSA-rpmj-rpgj-qmpm
CVE: CVE-2025-24898
CWE: CWE-416
Ecosystem: crates.io
CVSS: CVSS:4.0/AV:N/AC:H/AT:P/PR:N/UI:N/VC:L/VI:N/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-02-03
Source: https://github.com/advisories/GHSA-rpmj-rpgj-qmpm
Type: github-advisory

## Affected
- crates.io: `openssl` — affected >=0.10.0 <0.10.70

## Details
### Impact
`ssl::select_next_proto` can return a slice pointing into the `server` argument's buffer but with a lifetime bound to the `client` argument. In situations where the `server` buffer's lifetime is shorter than the `client` buffer's, this can cause a use after free. This could cause the server to crash or to return arbitrary memory contents to the client.

### Patches
`openssl` 0.10.70 fixes the signature of `ssl::select_next_proto` to properly constrain the output buffer's lifetime to that of both input buffers.

### Workarounds
In standard usage of `ssl::select_next_proto` in the callback passed to `SslContextBuilder::set_alpn_select_callback`, code is only affected if the `server` buffer is constructed *within* the callback. For example:

Not vulnerable - the server buffer has a `'static` lifetime:
```rust
builder.set_alpn_select_callback(|_, client_protos| {
    ssl::select_next_proto(b"\x02h2", client_protos).ok_or_else(AlpnError::NOACK)
});
```

Not vulnerable - the server buffer outlives the handshake:
```rust
let server_protos = b"\x02h2".to_vec();
builder.set_alpn_select_callback(|_, client_protos| {
    ssl::select_next_proto(&server_protos, client_protos).ok_or_else(AlpnError::NOACK)
});
```

Vulnerable - the server buffer is freed when the callback returns:
```rust
builder.set_alpn_select_callback(|_, client_protos| {
    let server_protos = b"\x02h2".to_vec();
    ssl::select_next_proto(&server_protos, client_protos).ok_or_else(AlpnError::NOACK)
});
```

### References
https://github.com/sfackler/rust-openssl/pull/2360

## References
- https://github.com/sfackler/rust-openssl/security/advisories/GHSA-rpmj-rpgj-qmpm
- https://nvd.nist.gov/vuln/detail/CVE-2025-24898
- https://github.com/sfackler/rust-openssl/pull/2360
- https://github.com/sfackler/rust-openssl/commit/f014afb230de4d77bc79dea60e7e58c2f47b60f2
- https://crates.io/crates/openssl
- https://github.com/sfackler/rust-openssl
- https://lists.debian.org/debian-lts-announce/2025/02/msg00009.html
- https://rustsec.org/advisories/RUSTSEC-2025-0004.html
