# [M] [actix-files] Panic triggered by empty Range header in GET request for static file

## Summary
Severity: Medium
Advisory: GHSA-gcqf-3g44-vc9p
CWE: CWE-20
Ecosystem: crates.io
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-02-06
Source: https://github.com/advisories/GHSA-gcqf-3g44-vc9p
Type: github-advisory

## Affected
- crates.io: `actix-files` — affected >=0 <0.6.10

## Details
### Summary
A GET request for a static file served by `actix-files` with an empty `Range` header triggers a panic. With `panic = "abort"`, a remote user may crash the process on-demand.

### Details
`actix-files` assumes that `HttpRange::parse()`, when `Ok`, always returns a vector with at least one element. When `parse()` is called on an empty string, it returns `Ok(vec![])`. This can cause a panic at named.rs:534 when handling an HTTP request with an empty `Range:` header. This shouldn't significantly impact programs built with the default `panic = "unwind"`, as the only effect is that the connection is closed when the worker thread panics and new threads are spooled up on demand. Programs built with `panic = "abort"` are vulnerable to being crashed on-demand by any user with permissions to perform a `GET` request for a static file served by `actix-files`.
https://github.com/actix/actix-web/blob/0383f4bdd1210e726143ca1ebcf01169b67a4b6c/actix-files/src/named.rs#L530-L535

### PoC
<details>
<summary>Minimal reproduction</summary>

`Cargo.toml`:
```toml
[package]
name = "example"
version = "0.1.0"
edition = "2021"

[dependencies]
actix-web = "=4.5.1"
actix-files = "=0.6.5"

[profile.dev]
panic = "abort"
```
`src/main.rs`:
```rust
use actix_files::NamedFile;
use actix_web::{get, Responder};

#[get("/")]
async fn index() -> impl Responder {
    NamedFile::open("test_file")
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    use actix_web::{App, HttpServer};

    HttpServer::new(|| App::new().service(index))
        .bind(("127.0.0.1", 8080))?
        .run()
        .await
}
```
`test.sh`:
```sh
#!/bin/bash

echo foo > test_file
cargo b
cargo r&
sleep 1
nc 127.0.0.1 8080 << EOF
GET / HTTP/1.1
Range:

EOF
kill %1
```

Create these files, then run `chmod +x test.sh && ./test.sh`. The server should start, then crash upon receiving the `GET` request from `netcat`.

This assumes a reasonably UNIX-like system with Rust, `bash` and `netcat` installed.
</details>

### Impact
It is believed that only programs compiled with panic = "abort" are affected significantly. The only potential impact that can be seen is Denial of Service, though an attacker able to repeatedly send GET requests without those requests getting blocked by rate limiting, DDoS protection, etc. would be able to keep a server down indefinitely. As only a single unblocked request is needed to trigger the panic, merely having a rate limiter may not be enough to prevent this.

Though the impact in the worst case is significant, the real-world risk of this vulnerability appears to be limited, as it would be expected that anyone for whom uptime is a significant concern would not compile their program with panic = "abort".

## References
- https://github.com/actix/actix-web/security/advisories/GHSA-gcqf-3g44-vc9p
- https://github.com/actix/actix-web
- https://github.com/actix/actix-web/blob/0383f4bdd1210e726143ca1ebcf01169b67a4b6c/actix-files/src/named.rs#L530-L535
