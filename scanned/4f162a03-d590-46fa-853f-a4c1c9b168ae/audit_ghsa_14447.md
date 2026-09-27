# [M] Comrak vulnerable to production of excessive output when parsing Markdown (GHSL-2023-048)

## Summary
Severity: Medium
Advisory: GHSA-xxmq-4vph-956w
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2023-03-28
Source: https://github.com/advisories/GHSA-xxmq-4vph-956w
Type: github-advisory

## Affected
- crates.io: `comrak` — affected >=0 <0.17.0

## Details
### Impact

comrak is vulnerable to the upstream cmark issue, ["Issue revealed by fuzzer"](https://github.com/commonmark/cmark/issues/354). A large number of references in a markdown document can trigger an overly large response.

### Patches

0.17.0 contains https://github.com/kivikakk/comrak/commit/70f97f3ea4eae30ffbd1b94c764a3de2f1c41d2a, which limits reference output to a 100Kb maximum.

### Workarounds

n/a

### References

* https://github.com/commonmark/cmark/issues/354

## References
- https://github.com/kivikakk/comrak/security/advisories/GHSA-xxmq-4vph-956w
- https://github.com/commonmark/cmark/issues/354
- https://github.com/kivikakk/comrak/commit/70f97f3ea4eae30ffbd1b94c764a3de2f1c41d2a
- https://github.com/kivikakk/comrak
- https://github.com/kivikakk/comrak/releases/tag/0.17.0
