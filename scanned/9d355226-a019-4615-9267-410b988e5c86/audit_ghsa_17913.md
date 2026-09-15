# [M] russh is missing overflow checks during channel windows adjust

## Summary
Severity: Medium
Advisory: GHSA-h5rc-j5f5-3gcm
CVE: CVE-2025-54804
CWE: CWE-190
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2025-08-04
Source: https://github.com/advisories/GHSA-h5rc-j5f5-3gcm
Type: github-advisory

## Affected
- crates.io: `russh` — affected >=0 <0.54.1

## Details
### Summary
The channel window adjust message of the SSH protocol is used to track the free space in the receive buffer of the other side of a channel. The current implementation takes the value from the message and adds it to an internal state value. This can result in a integer overflow. If the Rust code is compiled with overflow checks, it will panic.  A malicious  client can crash a server. 

### Details
According https://datatracker.ietf.org/doc/html/rfc4254#section-5.2, The value must not overflow. 
The incorrect handling is done in server/encrypted.rs and client/encrypted.rs in the handling of CHANNEL_WINDOW_ADJUST. 

```
let amount = map_err!(u32::decode(&mut r))?;
...
channel.recipient_window_size += amount;
```

It could be replaced with something like 

```
  if let Some(ref mut channel) = enc.channels.get_mut(&channel_num) {
                        // rfc 4254: The window MUST NOT be increased above 2^32 - 1 bytes.
                        new_size = channel.recipient_window_size.saturating_add(amount);
                        channel.recipient_window_size = new_size;
                    }
...
```

### PoC
A customized client code would be required to send a message with a big value like u32_max. Not done yet.

### Impact
This problem seems only critical to a server. One user can crash the server, which might take down the service. A malicious server could also crash a single client, but this seems not very critical.

## References
- https://github.com/Eugeny/russh/security/advisories/GHSA-h5rc-j5f5-3gcm
- https://nvd.nist.gov/vuln/detail/CVE-2025-54804
- https://github.com/Eugeny/russh/commit/0eb5e406780890e21ff71dd25d731b30676478e5
- https://github.com/Eugeny/russh
