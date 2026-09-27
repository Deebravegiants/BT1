# [H] Quinn affected by unauthenticated remote DoS via panic in QUIC transport parameter parsing

## Summary
Severity: High
Advisory: GHSA-6xvm-j4wr-6v98
CVE: CVE-2026-31812
CWE: CWE-248
Ecosystem: crates.io
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-11
Source: https://github.com/advisories/GHSA-6xvm-j4wr-6v98
Type: github-advisory

## Affected
- crates.io: `quinn-proto` — affected >=0 <0.11.14

## Details
### Summary
A remote, unauthenticated attacker can trigger a denial of service in applications using vulnerable `quinn` versions by sending a crafted QUIC Initial packet containing malformed `quic_transport_parameters`. `In quinn-proto` parsing logic, attacker-controlled varints are decoded with `unwrap()`, so truncated encodings cause `Err(UnexpectedEnd)` and `panic`. This is reachable over the network with a single packet and no prior trust or authentication.

### Details
The issue is panic-on-untrusted-input in QUIC transport parameter parsing.
In `quinn-proto` (observed in `quinn-proto 0.11.13`), parsing of some transport parameters uses a fallible varint decode followed by `unwrap()`. For malformed/truncated parameter values, decode returns `UnexpectedEnd`, and `unwrap()` panics.

#### Observed output:
```
thread 'tokio-rt-worker' (2366474) panicked at quinn-proto/src/transport_parameters.rs:473:67:
called `Result::unwrap()` on an `Err` value: UnexpectedEnd
```

### PoC
#### Reproduces against the upstream Quinn server example.
1. Start server:
```
cargo run --example server -- ./
```
2. Prepare PoC client environment:
```
python3 -m venv .venv
source .venv/bin/activate
pip install aioquic
```
3. Run PoC script [attack.py](https://github.com/user-attachments/files/25741713/attack.py) against server QUIC listener (default example target shown):
```
python attack.py
```
#### Observed output
```
thread 'tokio-rt-worker' (2366903) panicked at quinn-proto/src/transport_parameters.rs:473:67:
called `Result::unwrap()` on an `Err` value: UnexpectedEnd
```



### Impact
Vulnerability type: Remote Denial of Service (panic/crash)
Attack requirements:  Network reachability to UDP QUIC listener
Authentication/privileges: None
Who is impacted: Any server/application using affected `quinn/quinn-proto` versions where this parse path is reachable; process-level impact depends on integration panic handling policy


This vulnerability was originally submitted by @revofusion to the Ethereum Foundation bug bounty program

## References
- https://github.com/quinn-rs/quinn/security/advisories/GHSA-6xvm-j4wr-6v98
- https://nvd.nist.gov/vuln/detail/CVE-2026-31812
- https://github.com/quinn-rs/quinn/pull/2559
- https://github.com/quinn-rs/quinn
- https://rustsec.org/advisories/RUSTSEC-2026-0037.html
