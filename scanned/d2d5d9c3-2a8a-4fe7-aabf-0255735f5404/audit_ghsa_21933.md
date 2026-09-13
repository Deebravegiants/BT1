# [M] flynn/noise has improper nonce handling yielding potential state DoS

## Summary
Severity: Medium
Advisory: GHSA-g9mp-8g3h-3c5c
Ecosystem: Go
Published: 2022-02-15
Source: https://github.com/advisories/GHSA-g9mp-8g3h-3c5c
Type: github-advisory

## Affected
- Go: `github.com/flynn/noise` — affected >=0 <1.0.0

## Details
The Go package `github.com/flynn/noise`, a [Noise Protocol](https://noiseprotocol.org/) implementation, has two bugs in nonce handling in versions prior to v1.0.0.

### Issue 1: Potential nonce overflow

If 2<sup>64</sup> (~18.4 quintillion) or more messages are encrypted with `Encrypt` after handshaking, the nonce counter will wrap around, causing multiple messages to be encrypted with the same key and nonce, resulting in a potentially catastrophic weakening of the security properties of the symmetric cipher.

This has been resolved in the patched version by returning `ErrMaxNonce` from the `CipherState` `Encrypt` and `Decrypt` methods before the reserved maximum nonce is reached. If this error is encountered, the program should handshake again to start with a fresh `CipherState`.

### Issue 2: Potential denial of service via invalid ciphertext

If an attacker sends an invalid ciphertext into one peer's `Decrypt`, the nonce is incremented unconditionally. This causes a desync of the `CipherState` due to a nonce mismatch between the peers, resulting in a failure to decrypt all subsequent messages. A new handshake will be required to establish a new `CipherState`.

This has been resolved in the patched version by returning authentication errors from `Decrypt` before incrementing the nonce. 

### Patches

Fixed in https://github.com/flynn/noise/pull/44, tagged as v1.0.0.

### Acknowledgements

These issues were discovered during [an audit](https://www.bamsoftware.com/software/dnstt/cure53-turbotunnel-2021.pdf) of a user of this package ([dnstt](https://www.bamsoftware.com/software/dnstt/)). Thanks to UC Berkley for commissioning the audit, and to David Fifield and Nathan Brown for their collaboration on the fixes. The fixed issues are noted in the audit as:

* UCB-02-003 Potential nonce overflow in Noise protocol
* UCB-02-006 DoS due to unconditional nonce increment

## References
- https://github.com/flynn/noise/security/advisories/GHSA-g9mp-8g3h-3c5c
- https://github.com/flynn/noise/pull/44
- https://github.com/flynn/noise
- https://pkg.go.dev/vuln/GO-2022-0425
