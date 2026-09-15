# [M] Denosaurs emoji has ReDoS vulnerability in `replace` function

## Summary
Severity: Medium
Advisory: CVE-2023-30858
Aliases: GHSA-w2xx-hjhp-gx5v
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2023-04-28
Source: https://osv.dev/vulnerability/CVE-2023-30858
Type: osv

## Details
The Denosaurs emoji package provides emojis for dinosaurs. Starting in version 0.1.0 and prior to version 0.3.0, the reTrimSpace regex has 2nd degree polynomial inefficiency, leading to a delayed response given a big payload. The issue has been patched in 0.3.0. As a workaround, avoid using the `replace`, `unemojify`, or `strip` functions.

## References
- https://huntr.dev/bounties/444f2255-5085-466f-ba0e-5549fa8846a3/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/30xxx/CVE-2023-30858.json
- https://github.com/denosaurs/emoji/security/advisories/GHSA-w2xx-hjhp-gx5v
- https://nvd.nist.gov/vuln/detail/CVE-2023-30858
- https://github.com/denosaurs/emoji/pull/11
