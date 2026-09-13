# [?] fix(cli): fix jsonwebtoken panic (#14562)

## Summary
Severity: Unknown
Chain: Tooling
Component: foundry-rs/foundry
Published: 2026-05-04
Source: https://github.com/foundry-rs/foundry/commit/6e40f568f23ad36cb3ee8592b56a3ae7541211a7
Type: security-commit

## Details
fix(cli): fix jsonwebtoken panic (#14562)

`cast` panicked with this message coming from jsonwebtoken:

```
Call CryptoProvider::install_default() before this point to select a provider manually, or make sure exactly one of the
'rust_crypto' and 'aws_lc_rs' features is enabled.
See the documentation of the CryptoProvider type for more information.
```

This seemingly was introduced with the bump of jsonwebtoken to 10. Now
it requires you to pick one backend used by default controlled by the
compile time cargo features or call `CryptoProvider::install_default()`
at the beginning.

I realized that probably it would be better to just select the feature
and I picked `aws_lc_rs` as it seems to be increasingly a default and
we already are using the C toolchain.

Co-authored-by: zerosnacks <95942363+zerosnacks@users.noreply.github.com>
