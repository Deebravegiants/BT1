# [M] Ash string length constraints count graphemes, so a combining-mark string of any size passes max_length

## Summary
Severity: Medium
Advisory: CVE-2026-82752
Aliases: EEF-CVE-2026-82752, GHSA-cwjv-574p-59f6
CVSS: 6.0 (CVSS:4.0/AV:L/AC:L/AT:P/PR:N/UI:N/VC:N/VI:L/VA:H/SC:N/SI:N/SA:N)
Published: 2026-09-05
Source: https://osv.dev/vulnerability/CVE-2026-82752
Type: osv

## Details
Improper Validation of Specified Quantity in Input vulnerability in ash-project ash allows an attacker to store a value of arbitrary size in an attribute whose length constraint should bound it.

Ash measures string length with Elixir's String.length/1, which counts Unicode graphemes, in the max_length and min_length constraints of Ash.Type.String (apply_constraints/2 in lib/ash/type/string.ex), in Ash.Resource.Validation.StringLength, and in the string_length expression function. A grapheme carries an unbounded number of combining marks, so a base character followed by a million combining acute accents is one grapheme and megabytes of data, and satisfies max_length: 2. Where the data layer imposes no independent limit (ETS, Mnesia, or a Postgres text column) the whole value is persisted, so an attacker can write an entire request body into an attribute declared with a small maximum and grow storage without bound.

The counting unit also disagrees with the storage layer, which counts codepoints rather than graphemes, so a value accepted by the constraint can still be rejected or truncated by the column. A Postgres varchar(n) column bounds the value itself and is not exposed.

This issue affects ash: from 0.10.0 before 3.33.0.

## References
- https://cna.erlef.org/cves/CVE-2026-82752.html
- https://github.com
- https://osv.dev/vulnerability/EEF-CVE-2026-82752
- https://repo.hex.pm
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/82xxx/CVE-2026-82752.json
- https://github.com/ash-project/ash/security/advisories/GHSA-cwjv-574p-59f6
- https://nvd.nist.gov/vuln/detail/CVE-2026-82752
- https://github.com/ash-project/ash/commit/a64cab49b8886503e6b7c7b211d83c475aac48ca
- https://github.com/ash-project/ash/commit/cdbf4c4da6bda5f6f139078f01a64320b595216d
- https://github.com/ash-project/ash
