# [M] HTTPS MitM vulnerability due to lack of hostname verification

## Summary
Severity: Medium
Advisory: GHSA-9xjr-m6f3-v5wm
CVE: CVE-2016-10932
CWE: CWE-347
Ecosystem: crates.io
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-9xjr-m6f3-v5wm
Type: github-advisory

## Affected
- crates.io: `hyper` — affected >=0 <0.9.4

## Details
When used on Windows platforms, all versions of Hyper prior to 0.9.4 did not perform hostname verification when making HTTPS requests.

This allows an attacker to perform MitM attacks by preventing any valid CA-issued certificate, even if there's a hostname mismatch.

The problem was addressed by leveraging rust-openssl's built-in support for hostname verification.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-10932
- https://github.com/hyperium/hyper/issues/472
- https://github.com/hyperium/hyper/commit/01160abd92956e5f995cc45790df7a2b86c8989f
- https://github.com/hyperium/hyper/blob/master/CHANGELOG.md#v094-2016-05-09
- https://rustsec.org/advisories/RUSTSEC-2016-0002.html
