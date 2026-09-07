# [H] Wasmer filesystem sandbox not enforced

## Summary
Severity: High
Advisory: GHSA-4mq4-7rw3-vm5j
CVE: CVE-2023-51661
CWE: CWE-284
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-12-13
Source: https://github.com/advisories/GHSA-4mq4-7rw3-vm5j
Type: github-advisory

## Affected
- crates.io: `wasmer-cli` — affected >=3.0.0 <4.2.4

## Details
### Summary
As of Wasmer version v4.2.3, Wasm programs can access the filesystem outside of the sandbox.

### Details
https://github.com/wasmerio/wasmer/issues/4267

### PoC
A minimal Rust program:

```
fn main() {
    let f = std::fs::OpenOptions::new()
        .write(true)
        .create_new(true)
        .open("abc")
        .unwrap();
}
```

This should be compiled with `cargo build --target wasm32-wasi`. The compiled program, when run with wasmer WITHOUT `--dir`, can still create a file in the working directory.

### Impact
Service providers running untrusted Wasm code on Wasmer can unexpectedly expose the host filesystem.

## References
- https://github.com/wasmerio/wasmer/security/advisories/GHSA-4mq4-7rw3-vm5j
- https://nvd.nist.gov/vuln/detail/CVE-2023-51661
- https://github.com/wasmerio/wasmer/issues/4267
- https://github.com/wasmerio/wasmer/commit/4d63febf9d8b257b0531963b85df48d45d0dbf3c
- https://github.com/wasmerio/wasmer/commit/e3923612c23123025c26f982d390e34df7df030f
- https://github.com/wasmerio/wasmer
