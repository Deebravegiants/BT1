# [M] Symfony Vulnerable to SQL Injection in PdoAdapter::doClear() via Unsanitized $prefix

## Summary
Severity: Medium
Advisory: GHSA-6qh9-h6wf-jgqc
CVE: CVE-2026-45073
CWE: CWE-89
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:H/VA:L/SC:N/SI:N/SA:N/E:U (CVSS_V4)
Published: 2026-05-27
Source: https://github.com/advisories/GHSA-6qh9-h6wf-jgqc
Type: github-advisory

## Affected
- Packagist: `symfony/cache` — affected >=0 <5.4.52
- Packagist: `symfony/cache` — affected >=6.0.0 <6.4.40
- Packagist: `symfony/cache` — affected >=7.0.0 <7.4.12
- Packagist: `symfony/cache` — affected >=8.0.0 <8.0.12
- Packagist: `symfony/symfony` — affected >=0 <5.4.52
- Packagist: `symfony/symfony` — affected >=6.0.0 <6.4.40
- Packagist: `symfony/symfony` — affected >=7.0.0 <7.4.12
- Packagist: `symfony/symfony` — affected >=8.0.0 <8.0.12

## Details
### Description

`Symfony\Component\Cache\Adapter\PdoAdapter` is the PDO-backed cache adapter. Its `clear($prefix)` method (inherited from `AbstractAdapterTrait`) is documented to delete cache items whose key starts with `$prefix`.

In the non-versioning code path, the caller-supplied `$prefix` is concatenated into `$namespace = $this->namespace.$prefix` and passed to `PdoAdapter::doClear()`, which builds:

```sql
DELETE FROM <table> WHERE <id_col> LIKE '<namespace>%'
```

The value is interpolated directly into the SQL text and executed with `PDO::exec()`: `$namespace` is not bound. A caller able to influence `$prefix` can break out of the literal and inject SQL, expanding deletion scope from the intended prefix to arbitrary rows, or otherwise reshape query semantics.

Most applications don't expose `clear($prefix)` to untrusted input directly, but the contract of the method is to safely accept any prefix string, so the lack of escaping is a defect of the adapter itself.

### Resolution

`AbstractAdapterTrait::clear()` now rejects any `$prefix` containing characters outside `[-+.A-Za-z0-9]`: when an invalid prefix is supplied, the method logs a warning and returns `false` instead of reaching the SQL layer. This blocks quotes, `%`, null bytes and other characters that would let an attacker break out of the `LIKE` literal.

The patch for this issue is available [here](https://github.com/symfony/symfony/commit/ec50b799d79ebe24561f29351c1efcb6da95c9b1) for branch 5.4.

### Credits
Symfony would like to thank secsys_codex for reporting the issue and Nicolas Grekas for fixing it.

## References
- https://github.com/symfony/symfony/security/advisories/GHSA-6qh9-h6wf-jgqc
- https://github.com/symfony/symfony/commit/ec50b799d79ebe24561f29351c1efcb6da95c9b
- https://github.com/FriendsOfPHP/security-advisories/blob/master/symfony/cache/CVE-2026-45073.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/symfony/symfony/CVE-2026-45073.yaml
- https://github.com/symfony/symfony
- https://symfony.com/cve-2026-45073
