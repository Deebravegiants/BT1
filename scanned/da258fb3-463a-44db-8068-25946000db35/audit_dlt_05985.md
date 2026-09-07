# [?] bump rustls-webpki to 0.103.13 to clear RUSTSEC-2026-0098/0099/0104

## Summary
Severity: Unknown
Chain: Conflux
Component: Conflux-Chain/conflux-rust
Published: 2026-05-18
Source: https://github.com/Conflux-Chain/conflux-rust/commit/151ec5a47e717f3e09678f8fe2944a166d7db7ba
Type: security-commit

## Details
bump rustls-webpki to 0.103.13 to clear RUSTSEC-2026-0098/0099/0104

Three new advisories against rustls-webpki 0.103.10 (URI name
constraint, wildcard name constraint, CRL panic) are fixed in
0.103.12+. Master already runs 0.103.13; this aligns the PR lock.

The tracy-client-sys -> windows-targets re-resolve to 0.48.5 is a
benign collateral that matches master.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
