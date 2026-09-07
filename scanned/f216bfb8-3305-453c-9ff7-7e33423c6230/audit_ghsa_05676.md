# [H] Salvo is vulnerable to stored XSS in the list_html function by uploading files with malicious names

## Summary
Severity: High
Advisory: GHSA-54m3-5fxr-2f3j
CVE: CVE-2026-22257
CWE: CWE-79
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:L/A:L (CVSS_V3)
Published: 2026-01-08
Source: https://github.com/advisories/GHSA-54m3-5fxr-2f3j
Type: github-advisory

## Affected
- crates.io: `salvo` — affected >=0 <0.88.1

## Details
# Summary

The function `list_html` generates a file view of a folder without sanitizing the files or folders names, potentially leading to XSS in cases where a website allows access to public files using this feature, allowing  anyone to upload a file.

# Details

The vulnerable snippet of code is the following:
[**dir.rs**](https://github.com/salvo-rs/salvo/blob/16efeba312a274739606ce76366d921768628654/crates/serve-static/src/dir.rs#L581)

```rust
// ... fn list_html(...
        let mut link = "".to_owned();
        format!(
            r#"<a href="/">{}</a>{}"#,
            HOME_ICON,
            segments
                .map(|seg| {
                    link = format!("{link}/{seg}");
                    format!("/<a href=\"{link}\">{seg}</a>")
                })
                .collect::<Vec<_>>()
                .join("")
        )
// ...
```

# PoC

https://github.com/user-attachments/assets/1e161e17-f033-4cc4-855b-43fd38ed1be4

Here is the example app we used:

`mian.rs`
```rs
use salvo::prelude::*;
use salvo::serve_static::StaticDir;
use std::path::PathBuf;
use tokio::fs;

const INDEX_HTML: &str = r#"<!doctype html>
<html>
  <head><meta charset="utf-8"><title>StaticDir PoC</title></head>
  <body>
    <h2>Upload a file</h2>
    <form action="/upload" method="post" enctype="multipart/form-data">
      <input type="file" name="file" />
      <button type="submit">Upload</button>
    </form>

    <p>Browse uploads:</p>
    <ul>
      <li><a href="/files">/files</a></li>
      <li><a href="/files/">/files/</a></li>
    </ul>
  </body>
</html>
"#;

#[handler]
async fn index(res: &mut Response) {
    res.render(Text::Html(INDEX_HTML));
}

#[handler]
async fn upload(req: &mut Request, res: &mut Response) {
    fs::create_dir_all("uploads").await.expect("create uploads dir");

    let form = match req.form_data().await {
        Ok(v) => v,
        Err(e) => {
            res.status_code(StatusCode::BAD_REQUEST);
            res.render(Text::Plain(format!("form_data parse failed: {e}")));
            return;
        }
    };

    let Some(file_part) = form.files.get("file") else {
        res.status_code(StatusCode::BAD_REQUEST);
        res.render(Text::Plain("missing file field (name=\"file\")"));
        return;
    };

    let original_name = file_part.name().unwrap_or("upload.bin");

    let mut dest = PathBuf::from("uploads");
    dest.push(original_name);

    let tmp_path = file_part.path();
    if let Err(e) = fs::copy(tmp_path, &dest).await {
        res.status_code(StatusCode::INTERNAL_SERVER_ERROR);
        res.render(Text::Plain(format!("save failed: {e}")));
        return;
    }

    res.render(Text::Plain(format!(
        "Uploaded as: {original_name}\nNow open: http://127.0.0.1:5800/files/\n"
    )));
}

#[tokio::main]
async fn main() {
    tracing_subscriber::fmt().init();
    fs::create_dir_all("uploads").await.expect("create uploads dir");

    let router = Router::new()
        .get(index)
        .push(Router::with_path("upload").post(upload))
        .push(
            Router::with_path("files/{**rest_path}")
                .get(StaticDir::new("uploads").auto_list(true)),
        );

    let acceptor = TcpListener::new("127.0.0.1:5800").bind().await;
    Server::new(acceptor).serve(router).await;
}
```
`Cargo.toml`
```rs
[package]
name = "poc"
version = "0.1.0"
edition = "2024"

[dependencies]
salvo = { version = "0.85.0", features = ["serve-static"] }
tokio = { version = "1", features = ["macros", "rt-multi-thread", "fs"] }
tracing-subscriber = "0.3"
```
# Impact

JavaScript execution, most likely leading to an account takeover, depending on the site's constraint (CSP, etc…).

## References
- https://github.com/salvo-rs/salvo/security/advisories/GHSA-54m3-5fxr-2f3j
- https://nvd.nist.gov/vuln/detail/CVE-2026-22257
- https://github.com/salvo-rs/salvo
- https://github.com/salvo-rs/salvo/blob/16efeba312a274739606ce76366d921768628654/crates/serve-static/src/dir.rs#L581
