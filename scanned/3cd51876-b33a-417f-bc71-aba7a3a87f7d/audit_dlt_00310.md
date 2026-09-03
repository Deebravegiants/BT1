# [H] EL-2026-21: DoS via malicious p2p handshake with invalid secp256k1 public key

## Summary
Severity: High
Chain: Ethereum (execution layer)
Component: Geth
Source: https://notes.ethereum.org/TxnXevM4QUW7ILp34nIdyQ
Type: ef-disclosure

## Details
DoS via malicious p2p message

Package
github.com/ethereum/go-ethereum (
Go
)
Affected versions
>= 1.14.0, < 1.14.13
Patched versions
>= 1.14.13
Description
Impact

A vulnerable node can be forced to shutdown/crash using a specially crafted message.

During the peer-to-peer connection handshake, a shared secret key is computed. The implementation
did not verify whether the EC public key provided by the remote party is a valid point on the secp256k1 curve.
By simply sending an all-zero public key, a crash could be induced due to unexpected results from the handshake.

The issue was fixed by adding a curve point validity check in 159fb1a
Patches

A fix has been included in geth version 1.14.13 and onwards.

Fix:
Add this to crypto.go
if !S256().IsOnCurve(x, y) {
		return nil, errInvalidPubkey
	}
