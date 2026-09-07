# [M] Decimal: Unbounded exponent in `Decimal.new` enables unauthenticated DoS

## Summary
Severity: Medium
Advisory: GHSA-rhv4-8758-jx7v
CVE: CVE-2026-32686
CWE: CWE-400
Ecosystem: Hex
CVSS: CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-05-12
Source: https://github.com/advisories/GHSA-rhv4-8758-jx7v
Type: github-advisory

## Affected
- Hex: `decimal` — affected >=0.1.0 <3.0.0

## Details
Summary
`decimal` doesn't bound the exponent on parsed input, so something like `"1e10000000"` is parsed fine but then explodes the memory to more than 7GB if you run e.g. `Decimal.add(Decimal.parse("1e10000000"), 1)` because for positive `exp`, the function tail-recurses with `coef * 10` and `exp - 1` per iteration, growing the bignum coefficient by one digit each step. In the worst case, one request is enough to OOM the BEAM.

### Details
`Decimal.new/parse/cast` happily store huge exponents. After that, a bunch of core paths allocate proportional to `exp`:
- `add/sub/div` go through `add_align`, which calls `pow10(exp1 - exp2)` and builds a giant bignum (lib/decimal.ex:1734-1738, 1827).
- `to_string/2` with `:normal` (also `:xsd` and the `String.Chars` impl) does `:lists.duplicate(exp, ?0)` (lib/decimal.ex:1506, 1513).
- `to_integer/1` recurses `coef * 10`, `exp - 1` once per unit of `exp` (lib/decimal.ex:1603-1605).
- `round/3` does the same `:lists.duplicate` trick on the exp difference (lib/decimal.ex:1850, 1874).
- `compare/3` with a threshold argument loops back into `add`/`sub`, so it's vulnerable too (lib/decimal.ex:331-332).

### PoC
Any of these will hang or OOM the BEAM:
```elixir
Decimal.add(Decimal.new("1"), Decimal.new("1e1000000000"))
Decimal.to_string(Decimal.new("1e1000000000"), :normal)
Decimal.to_integer(Decimal.new("1e1000000000"))
Decimal.round(Decimal.new("1e1000000000"))
```

### Impact
Unauthenticated remote DoS. Anything that takes a user-supplied decimal (JSON, form field, Ecto `:decimal` field — basically everywhere) and then does arithmetic, rounding, `to_integer`, or `to_string` on it is exposed. One request can kill the node with a Out-of-Memory exception.

### Note on the security fixes done in version 2.4.0
While `2.4.0` has the changes to mitigate this issue it's not considered as a patched version because it doesn't have them enabled by default.

## References
- https://github.com/ericmj/decimal/security/advisories/GHSA-rhv4-8758-jx7v
- https://nvd.nist.gov/vuln/detail/CVE-2026-32686
- https://github.com/ericmj/decimal/commit/6a523f3a73b8c9974540e21c7aa88f1258bb35ae
- https://cna.erlef.org/cves/CVE-2026-32686.html
- https://github.com/ericmj/decimal
- https://github.com/ericmj/decimal/releases/tag/v2.4.0
- https://github.com/ericmj/decimal/releases/tag/v3.0.0
- https://osv.dev/vulnerability/EEF-CVE-2026-32686
