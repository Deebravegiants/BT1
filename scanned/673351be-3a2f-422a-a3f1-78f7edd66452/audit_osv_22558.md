# [H] CVE-2022-31394

## Summary
Severity: High
Advisory: CVE-2022-31394
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-02-21
Source: https://osv.dev/vulnerability/CVE-2022-31394
Type: osv

## Details
Hyperium Hyper before 0.14.19 does not allow for customization of the max_header_list_size method in the H2 third-party software, allowing attackers to perform HTTP2 attacks.

## References
- https://github.com/hyperium/hyper/compare/v0.14.18...v0.14.19
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/31xxx/CVE-2022-31394.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-31394
- https://github.com/hyperium/hyper/issues/2826
- https://github.com/hyperium/hyper/pull/2828
