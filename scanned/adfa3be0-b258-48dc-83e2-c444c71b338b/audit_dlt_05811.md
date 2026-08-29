# [?] Prevent unsoundness in environments with broken `madvise(MADV_DONTNEED)` (#11722)

## Summary
Severity: Unknown
Chain: Polkadot
Component: paritytech/substrate
Published: 2022-06-28
Source: https://github.com/paritytech/substrate/commit/ee3eb8f2448cc1bb978c5d1564febd351c128bb0
Type: security-commit

## Details
Prevent unsoundness in environments with broken `madvise(MADV_DONTNEED)` (#11722)

* Prevend unsoundness in environments with broken `madvise(MADV_DONTNEED)`

* Add the `std` feature to `rustix` dependency

Apparently not having this breaks compilation on non-nightly toolchains.

* Autodetect the page size when checking whether `madvise` works

* Only make sure that the madvice check doesn't return `Err`
