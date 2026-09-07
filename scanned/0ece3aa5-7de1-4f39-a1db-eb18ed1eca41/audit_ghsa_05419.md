# [H] Salvo is vulnerable to reflected XSS in the list_html function

## Summary
Severity: High
Advisory: GHSA-rjf8-2wcw-f6mp
CVE: CVE-2026-22256
CWE: CWE-79
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:L/A:L (CVSS_V3)
Published: 2026-01-08
Source: https://github.com/advisories/GHSA-rjf8-2wcw-f6mp
Type: github-advisory

## Affected
- crates.io: `salvo` — affected >=0 <0.88.1

## Details
# Summary

The function `list_html` generates an file view of a folder which includes a render of the current path, in which its inserted in the HTML without proper sanitation, leading to reflected XSS. The request path is decoded and normalized in the matching stage but is not inserted raw in the HTML view (current.path). The only constraint here is for the root path (e.g., /files in the PoC example) to have a subdirectory (e. g., common ones like styles/scripts/etc.) so that the matching returns the list HTML page instead of the Not Found page.

# Details

The vulnerable snippet of code is the following:
[**dir.rs**](https://github.com/salvo-rs/salvo/blob/16efeba312a274739606ce76366d921768628654/crates/serve-static/src/dir.rs#L593)

```rust
// ... fn list_html(...
    let mut ftxt = format!(
        r#"<!DOCTYPE html><html><head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width">
        <title>{}</title>
        <style>{}</style></head><body><header><h3>Index of: {}</h3></header><hr/>"#,
        current.path,
        HTML_STYLE,
        header_links(&current.path)
    );
// ...
```

As seen here `<title>{}</title>` it is inserted unsafely.

# PoC

https://github.com/user-attachments/assets/92a29a67-547b-40a5-af26-f1b0dd332702

Here is the example app, note this doesn’t need an upload feature (e.g to the other reported vulnerability), only the sub-folder is required.

`main.rs`
```rust
use salvo::prelude::*;
use salvo::serve_static::StaticDir;
use tokio::fs;

#[tokio::main]
async fn main() {
    tracing_subscriber::fmt().init();
    fs::create_dir_all("uploads").await.expect("create uploads dir");

    let router = Router::new()
        .push(
            Router::with_path("files/{**rest_path}")
                .get(StaticDir::new("uploads").auto_list(true)),
        );

    let acceptor = TcpListener::new("127.0.0.1:5800").bind().await;
    Server::new(acceptor).serve(router).await;
}
```

`Cargo.toml`
```rust
[package]
name = "salvo-staticdir-xss-poc"
version = "0.1.0"
edition = "2024"

[dependencies]
salvo = { version = "0.85.0", features = ["serve-static"] }
tokio = { version = "1", features = ["macros", "rt-multi-thread", "fs"] }
tracing-subscriber = "0.3"
```

Setup commands:
```bash
mkdir uploads
mkdir uploads/bla
```

# Impact

JavaScript execution, most likely leading to an account takeover, depending on the site's constraint (CSP, etc…).

## References
- https://github.com/salvo-rs/salvo/security/advisories/GHSA-rjf8-2wcw-f6mp
- https://nvd.nist.gov/vuln/detail/CVE-2026-22256
- https://github.com/salvo-rs/salvo
- https://github.com/salvo-rs/salvo/blob/16efeba312a274739606ce76366d921768628654/crates/serve-static/src/dir.rs#L593
