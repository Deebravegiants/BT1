# [H] Infinite loop in github.com/btcsuite/go-socks

## Summary
Severity: High
Advisory: GO-2020-0024
Aliases: CVE-2013-10005, GHSA-gxgj-xjcw-fv9p
Package: github.com/btcsuite/go-socks
Published: 2021-04-14
Source: https://osv.dev/vulnerability/GO-2020-0024
Type: chain-advisory

## Affected
- Go: `github.com/btcsuite/go-socks` — affected >=0 <0.0.0-20130808000456-233bccbb1abe
- Go: `github.com/btcsuitereleases/go-socks` — affected >=0 <0.0.0-20130808000456-233bccbb1abe

## Details
The RemoteAddr and LocalAddr methods on the returned net.Conn may call themselves, leading to an infinite loop which will crash the program due to a stack overflow.

## References
- https://github.com/btcsuite/go-socks/commit/233bccbb1abe02f05750f7ace66f5bffdb13defc
