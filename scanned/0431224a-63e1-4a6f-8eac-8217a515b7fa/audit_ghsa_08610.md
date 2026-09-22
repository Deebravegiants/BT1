# [C] Marten has an injection vulnerability in its full-text search regConfig parameter

## Summary
Severity: Critical
Advisory: GHSA-vmw2-qwm8-x84c
CVE: CVE-2026-45288
CWE: CWE-74, CWE-89
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-05-14
Source: https://github.com/advisories/GHSA-vmw2-qwm8-x84c
Type: github-advisory

## Affected
- NuGet: `Marten` — affected >=0 <8.37.0

## Details
## Summary

Marten's full-text search APIs interpolated the user-supplied `regConfig` parameter directly into the generated SQL without parameterization or validation, making every code path that exposes `regConfig` to untrusted input a SQL injection sink.

## Affected APIs

- `IQuerySession.SearchAsync<T>(string searchTerm, string regConfig, ...)`
- `IQuerySession.PlainTextSearchAsync<T>(...)`
- `IQuerySession.PhraseSearchAsync<T>(...)`
- `IQuerySession.WebStyleSearchAsync<T>(...)`
- `IQuerySession.PrefixSearchAsync<T>(...)`
- `IQueryable<T>.Where(x => x.Search(term, regConfig))` and the matching `PlainTextSearch` / `PhraseSearch` / `WebStyleSearch` / `PrefixSearch` extension methods

## Details

In the affected versions, [`FullTextWhereFragment`](https://github.com/JasperFx/marten/blob/master/src/Marten/Linq/SqlGeneration/Filters/FullTextWhereFragment.cs) renders the WHERE-clause SQL by string interpolation:

```csharp
private string Sql =>
    $"to_tsvector('{_regConfig}'::regconfig, {_dataConfig}) @@ {_searchFunction}('{_regConfig}'::regconfig, ?)";
```

`_regConfig` arrives unchanged from the public API surface above. Any value containing a single quote terminates the SQL literal and lets an attacker append arbitrary PostgreSQL.

### Confirmed exploit shapes (with `regConfig` set to attacker-controlled input)

| Goal | Payload |
| --- | --- |
| Time-based blind | `english'::text); SELECT pg_sleep(5); --` |
| Information disclosure | `english'; SELECT version(); --` |
| DDL execution | `english'; DROP TABLE mt_doc_article; --` |

All five overloads listed above produced SQL containing the verbatim payload.

## Impact

- **Confidentiality**: an attacker can append arbitrary `SELECT` statements and exfiltrate database contents through error channels, response timing, or — if the application surfaces query results — directly.
- **Integrity / Availability**: DDL, `UPDATE`, `DELETE`, and `pg_sleep`-style denial-of-service payloads succeed under the same vector. Concrete impact depends on the database role used by the Marten connection string.
- **Precondition**: the calling application must forward attacker-controlled input into the `regConfig` parameter (e.g. a `?lang=` query string mapped to `regConfig`). Applications that hard-code `regConfig` to a compile-time constant are not exploitable.

## Patches

Fixed in **Marten 8.36.1** (and forward) by [#4343](https://github.com/JasperFx/marten/pull/4343).

`FullTextWhereFragment` now validates `regConfig` against `^[a-zA-Z_][a-zA-Z0-9_]*(\.[a-zA-Z_][a-zA-Z0-9_]*)?$` (a simple PostgreSQL identifier, optionally schema-qualified, capped at `NAMEDATALEN-1` per side) and throws `ArgumentException` for anything else. The default value (`"english"`), schema-qualified configs (`"pg_catalog.english"`), and the standard PostgreSQL text-search configurations all continue to work.

## Workarounds

If users cannot upgrade immediately, do **one** of the following at the application boundary:

1. Hard-code `regConfig` to a compile-time constant (`"english"`, `"simple"`, …) and never accept it from request input.
2. Validate any externally-sourced `regConfig` value before passing it to Marten — e.g. against the same regex as the patch (`^[a-zA-Z_][a-zA-Z0-9_]*(\.[a-zA-Z_][a-zA-Z0-9_]*)?$`) or against an allowlist of PostgreSQL configurations the application actually uses.
3. Drop the `regConfig` argument from the call site so Marten falls back to the safe default.

## Resources

- Patch PR: [JasperFx/marten#4343](https://github.com/JasperFx/marten/pull/4343)
- Patched file: [`FullTextWhereFragment.cs`](https://github.com/JasperFx/marten/blob/master/src/Marten/Linq/SqlGeneration/Filters/FullTextWhereFragment.cs)
- Regression tests: [`full_text_regconfig_sql_injection.cs`](https://github.com/JasperFx/marten/blob/master/src/LinqTests/Bugs/full_text_regconfig_sql_injection.cs)
- CWE-89: <https://cwe.mitre.org/data/definitions/89.html>

## Credit

Reported privately to the JasperFx team with a working proof of concept covering all five affected overloads.

## References
- https://github.com/JasperFx/marten/security/advisories/GHSA-vmw2-qwm8-x84c
- https://nvd.nist.gov/vuln/detail/CVE-2026-45288
- https://github.com/JasperFx/marten/pull/4343
- https://github.com/JasperFx/marten/commit/626249656829860b9c55895b5b6046b61a2a695f
- https://github.com/JasperFx/marten
