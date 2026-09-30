# [H] Large RSA keys can cause high resource usage in github.com/libp2p/go-libp2p

## Summary
Severity: High
Advisory: GO-2023-2000
Aliases: CVE-2023-39533, GHSA-876p-8259-xjgg
Package: github.com/libp2p/go-libp2p
Published: 2023-08-08
Source: https://osv.dev/vulnerability/GO-2023-2000
Type: chain-advisory

## Affected
- Go: `github.com/libp2p/go-libp2p` — affected >=0.29.0 <0.29.1

## Details
Large RSA keys can lead to resource exhaustion attacks.

With fix, the size of RSA keys transmitted during handshakes is restricted to <= 8192 bits.

## References
- https://github.com/libp2p/go-libp2p/security/advisories/GHSA-876p-8259-xjgg
- https://go.dev/issue/61460
- https://github.com/libp2p/go-libp2p/commit/0cce607219f3710addc7e18672cffd1f1d912fbb
