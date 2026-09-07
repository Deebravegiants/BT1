# [M] Buffa has a Use-After-Free in OwnedView via Unsound 'static Lifetime Promotion in Deref

## Summary
Severity: Medium
Advisory: GHSA-9pwq-gcrx-wghh
CVE: CVE-2026-55406
CWE: CWE-200, CWE-416
Ecosystem: crates.io
CVSS: CVSS:4.0/AV:L/AC:H/AT:P/PR:N/UI:N/VC:H/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-08-28
Source: https://github.com/advisories/GHSA-9pwq-gcrx-wghh
Type: github-advisory

## Affected
- crates.io: `buffa` — affected >=0 <0.7.0

## Details
A soundness bug in `buffa`'s `OwnedView<V>` allowed safe Rust code to trigger a use-after-free. The `OwnedView::decode` constructor transmuted a borrowed slice to `&'static [u8]`, and the `Deref` implementation exposed the promoted `'static` lifetime on borrowed view fields (such as `&'static str` and `&'static [u8]`) to callers. Because these references appeared to be `'static`, the borrow checker permitted them to outlive the `OwnedView`; once the `OwnedView` was dropped and its backing buffer freed, those references became dangling, enabling memory corruption, information disclosure of freed heap contents, and cross-thread misuse — all without any `unsafe` code in the calling application. Users are advised to update to the latest patched version of buffa.

Thank you to hackerone.com/suul for reporting this issue.

## References
- https://github.com/anthropics/buffa/security/advisories/GHSA-9pwq-gcrx-wghh
- https://nvd.nist.gov/vuln/detail/CVE-2026-55406
- https://github.com/anthropics/buffa/pull/154
- https://github.com/anthropics/buffa/commit/7dcf50a1a40eca6ed8d6c6dd59f4310aa0d68b0e
- https://github.com/anthropics/buffa
- https://github.com/anthropics/buffa/releases/tag/v0.7.0
