# [C] libnftnl has Heap-based Buffer Overflow in nftnl::Batch::with_page_size (nftnl-rs)

## Summary
Severity: Critical
Advisory: GHSA-2fjw-whxm-9v4q
CWE: CWE-122
Ecosystem: crates.io
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:L/SA:N (CVSS_V4)
Published: 2025-11-25
Source: https://github.com/advisories/GHSA-2fjw-whxm-9v4q
Type: github-advisory

## Affected
- crates.io: `nftnl` — affected >=0 <0.9.0

## Details
A heap-buffer-overflow vulnerability exists in the Rust wrapper for libnftnl, triggered via the nftnl::Batch::with_page_size constructor. When a small or malformed page size is provided, the underlying C code allocates an insufficient buffer, leading to out-of-bounds writes during batch initialization.

The flaw was fixed in commit 94a286f by adding an overflow check:
```Rust
batch_page_size
    .checked_add(crate::nft_nlmsg_maxsize())
    .expect("batch_page_size is too large and would overflow");
```

## References
- https://github.com/mullvad/nftnl-rs/issues/76#issue-3528876468
- https://github.com/mullvad/nftnl-rs/commit/94a286f87e88f431913d19668246de9006790125
- https://github.com/mullvad/nftnl-rs
- https://rustsec.org/advisories/RUSTSEC-2025-0126.html
