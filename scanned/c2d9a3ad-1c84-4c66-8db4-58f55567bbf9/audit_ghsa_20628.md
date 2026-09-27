# [H] Rust-WebSocket memory allocation based on untrusted length

## Summary
Severity: High
Advisory: GHSA-qrjv-rf5q-qpxc
CVE: CVE-2022-35922
CWE: CWE-119, CWE-400, CWE-770
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-08-06
Source: https://github.com/advisories/GHSA-qrjv-rf5q-qpxc
Type: github-advisory

## Affected
- crates.io: `websocket` — affected >=0 <0.26.5

## Details
## Impact
Untrusted websocket connections can cause an out-of-memory (OOM) process abort in a client or a server.
The root cause of the issue is during dataframe parsing.
Affected versions would allocate a buffer based on the declared dataframe size, which may come from an untrusted source.
When `Vec::with_capacity` fails to allocate, the default Rust allocator will abort the current process, killing all threads. This affects only sync (non-Tokio) implementation. Async version also does not limit memory, but does not use `with_capacity`, so DoS can happen only when bytes for oversized dataframe or message actually got delivered by the attacker.

This is a security concern for you, if
- your server application handles untrusted websocket connections
- OR your client application connects to untrusted websocket servers

## Patches
The crashes are fixed in version **0.26.5** by imposing default dataframe size limits.
Affected users are advised to update to this version.

Note that default memory limits are rather large (100MB dataframes and 200 MB messages), so they can still cause DoS in some environments (i.e. 32-bit). New API has been added to fine tune those limits for specific applications.

### Workarounds

* Migrate your project to another, maintained Websocket library like Tungstenite.
* Accept only trusted WebSocket traffic.
* Filter the WebSocket traffic though some kind of proxy that ensures sanity limits on messages.
* Handle process aborts gracefully and limit process memory using OS tools.


## Credits
This issue was reported by [Evan Richter](https://github.com/evanrichter) at ForAllSecure and found with [Mayhem](https://forallsecure.com/mayhem-for-code) and [Cargo Fuzz](https://github.com/rust-fuzz/cargo-fuzz).

## References
- https://github.com/websockets-rs/rust-websocket/security/advisories/GHSA-qrjv-rf5q-qpxc
- https://nvd.nist.gov/vuln/detail/CVE-2022-35922
- https://github.com/websockets-rs/rust-websocket/commit/cbf6e9983e839d2ecad86de8cd1b3f20ed43390b
- https://github.com/websockets-rs/rust-websocket
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/4V2EOOU5OLEHVMKAH6BALQXKDKIZRXCI
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/HYPNCM4H4OFBIZI6XMJ2DUTS54FT2TWP
- https://rustsec.org/advisories/RUSTSEC-2022-0035.html
