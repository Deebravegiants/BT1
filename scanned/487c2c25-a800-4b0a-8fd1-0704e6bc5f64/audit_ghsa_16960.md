# [H] cassandra-rs's non-idiomatic use of iterators leads to use after free

## Summary
Severity: High
Advisory: GHSA-x9xc-63hg-vcfq
CVE: CVE-2024-27284
CWE: CWE-416
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2024-04-05
Source: https://github.com/advisories/GHSA-x9xc-63hg-vcfq
Type: github-advisory

## Affected
- crates.io: `cassandra-cpp` — affected >=0 <3.0.0

## Details
### Impact
Code that attempts to use an item (e.g., a row) returned by an iterator after the iterator has advanced to the next item will be accessing freed memory and experience undefined behaviour. Code that uses the item and then advances the iterator is unaffected. This problem has always existed.

This is a use-after-free bug, so it's rated high severity. If your code uses a pre-3.0.0 version of cassandra-rs, and uses an item returned by a cassandra-rs iterator after calling `next()` on that iterator, then it is vulnerable. However, such code will almost always fail immediately - so we believe it is unlikely that any code using this pattern would have reached production. For peace of mind, we recommend you upgrade anyway.

### Patches
The problem has been fixed in version 3.0.0. Users should upgrade to ensure their code cannot use the problematic pattern.

### Workarounds
Ensure all usage fits the expected pattern. For example, use `get_first_row()` rather than an iterator, or completely process an item before advancing the iterator with `next()`.

### References
None.

## References
- https://github.com/Metaswitch/cassandra-rs/security/advisories/GHSA-x9xc-63hg-vcfq
- https://nvd.nist.gov/vuln/detail/CVE-2024-27284
- https://github.com/Metaswitch/cassandra-rs/commit/ae054dc8044eac9c2c7ae2b1ab154b53ca7f8df7
- https://github.com/Metaswitch/cassandra-rs
- https://rustsec.org/advisories/RUSTSEC-2024-0017.html
