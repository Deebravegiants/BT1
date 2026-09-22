# [M] Saleor: Customers' addresses leak when using Warehouse as a `Pickup: Local stock only` delivery method

## Summary
Severity: Medium
Advisory: GHSA-mrj3-f2h4-7w45
CVE: CVE-2024-29888
CWE: CWE-359
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2024-03-28
Source: https://github.com/advisories/GHSA-mrj3-f2h4-7w45
Type: github-advisory

## Affected
- PyPI: `saleor` — affected >=3.14.56 <3.14.61
- PyPI: `saleor` — affected >=3.15.31 <3.15.37
- PyPI: `saleor` — affected >=3.16.27 <3.16.34
- PyPI: `saleor` — affected >=3.17.25 <3.17.32
- PyPI: `saleor` — affected >=3.18.19 <3.18.28
- PyPI: `saleor` — affected >=3.19.5 <3.19.15

## Details
### Summary
Using `Pickup: Local stock only` as a click-and-collect points could cause a leak of customer addresses

### Details
When using `Pickup: Local stock only` click-and-collect as a delivery method in specific conditions the customer could overwrite the warehouse address with its own, which exposes its address as click-and-collect address.

### Impact
The vulnerability can cause the leak of customer's address when using click-and-collect delivery option marked as `Local stock only`. It has impact on all orders with click-and-collect delivery method marked as `Pickup:Local stock only`
The affected versions: `>=3.14.56 <3.14.61`, `>=3.15.31 <3.15.37`, `>=3.16.27 <3.16.34`, `>=3.17.25 <3.17.32`, `>=3.18.19 <3.18.28`, `>=3.19.5 <3.19.15`
This issue has been patched in versions: `3.14.61`, `3.15.37`, `3.16.34`, `3.17.32`, `3.18.28`, `3.19.15`


### Workaround
We strongly recommend upgrading to the latest versions, in case of inability to upgrade straight away, possible workarounds are:
- turn off click-and-collect delivery method on warehouse view when `Pickup` option is set to `Local stock only`.
- cherry-pick the changes from PRs: https://github.com/saleor/saleor/pull/15694 & https://github.com/saleor/saleor/pull/15697

### References
- Commits introducing the issue (https://github.com/saleor/saleor/commit/22a1aa3ef0bc54156405f69146788016a7f3f761 main, https://github.com/saleor/saleor/commit/997f7ea4f576543ec88679a86bfe1b14f7f2ff26 3.14, https://github.com/saleor/saleor/commit/ef003c76a304c89ddb2dc65b7f1d5b3b2ba1c640 3.15, https://github.com/saleor/saleor/commit/39abb0f4e4fe6503f81bfbb871227e4f70bcdd5c 3.16, https://github.com/saleor/saleor/commit/b7cecda8b603f7472790150bb4508c7b655946d4 3.17, https://github.com/saleor/saleor/commit/dccc2c842b4e2e09470929c80f07dc137e439182 3.18, https://github.com/saleor/saleor/commit/d8ba545c16ad3153febc5b5be8fd2ef75da9fc95 3.19)
- https://github.com/saleor/saleor/commit/47cedfd7d6524d79bdb04708edcdbb235874de6b (main branch)
https://github.com/saleor/saleor/releases/tag/3.14.60
https://github.com/saleor/saleor/releases/tag/3.14.61
https://github.com/saleor/saleor/releases/tag/3.15.36
https://github.com/saleor/saleor/releases/tag/3.15.37
https://github.com/saleor/saleor/releases/tag/3.16.33
https://github.com/saleor/saleor/releases/tag/3.16.34
https://github.com/saleor/saleor/releases/tag/3.17.31
https://github.com/saleor/saleor/releases/tag/3.17.32
https://github.com/saleor/saleor/releases/tag/3.18.27
https://github.com/saleor/saleor/releases/tag/3.18.28
https://github.com/saleor/saleor/releases/tag/3.19.14
https://github.com/saleor/saleor/releases/tag/3.19.15

## References
- https://github.com/saleor/saleor/security/advisories/GHSA-mrj3-f2h4-7w45
- https://nvd.nist.gov/vuln/detail/CVE-2024-29888
- https://github.com/saleor/saleor/pull/15697
- https://github.com/saleor/saleor/pull/15694
- https://github.com/saleor/saleor/commit/47cedfd7d6524d79bdb04708edcdbb235874de6b
- https://github.com/saleor/saleor/commit/997f7ea4f576543ec88679a86bfe1b14f7f2ff26
- https://github.com/saleor/saleor/commit/b7cecda8b603f7472790150bb4508c7b655946d4
- https://github.com/saleor/saleor/commit/d8ba545c16ad3153febc5b5be8fd2ef75da9fc95
- https://github.com/saleor/saleor/commit/dccc2c842b4e2e09470929c80f07dc137e439182
- https://github.com/saleor/saleor/commit/ef003c76a304c89ddb2dc65b7f1d5b3b2ba1c640
- https://github.com/saleor/saleor/commit/39abb0f4e4fe6503f81bfbb871227e4f70bcdd5c
- https://github.com/saleor/saleor/commit/22a1aa3ef0bc54156405f69146788016a7f3f761
- https://github.com/saleor/saleor/releases/tag/3.14.61
- https://github.com/saleor/saleor/releases/tag/3.15.37
- https://github.com/saleor/saleor/releases/tag/3.16.34
- https://github.com/saleor/saleor/releases/tag/3.17.32
- https://github.com/saleor/saleor/releases/tag/3.18.28
- https://github.com/saleor/saleor/releases/tag/3.19.15
- https://github.com/saleor/saleor
- https://github.com/pypa/advisory-database/tree/main/vulns/saleor/PYSEC-2026-1890.yaml
