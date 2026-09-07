# [M] Symfony: UrlGenerator Dot-Segment Encoding Skips Every Other Chained `../` or `./` → Generated URL Collapses Off-Route Under RFC 3986 Normalization

## Summary
Severity: Medium
Advisory: GHSA-h5x3-xfc9-m39h
CVE: CVE-2026-48784
CWE: CWE-172, CWE-601
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:L/VA:N/SC:L/SI:L/SA:N (CVSS_V4)
Published: 2026-06-15
Source: https://github.com/advisories/GHSA-h5x3-xfc9-m39h
Type: github-advisory

## Affected
- Packagist: `symfony/routing` — affected >=0 <5.4.53
- Packagist: `symfony/routing` — affected >=6.0.0 <6.4.41
- Packagist: `symfony/routing` — affected >=7.0.0 <7.4.13
- Packagist: `symfony/routing` — affected >=8.0.0 <8.0.13
- Packagist: `symfony/symfony` — affected >=0 <5.4.53
- Packagist: `symfony/symfony` — affected >=6.0.0 <6.4.41
- Packagist: `symfony/symfony` — affected >=7.0.0 <7.4.13
- Packagist: `symfony/symfony` — affected >=8.0.0 <8.0.13

## Details
### Description

`Symfony\Component\Routing\Generator\UrlGenerator::doGenerate()` percent-encodes `.` and `..` path segments so that the generated URL still resolves to the originating route after RFC 3986 §5.2.4 dot-segment removal (which strict RFC-3986 consumers — routers, reverse proxies, HTTP clients — perform *before* percent-decoding).

The encoding was implemented as `strtr($url, ['/../' => '/%2E%2E/', '/./' => '/%2E/'])` plus a trailing-segment fixup. `strtr` advances past the trailing `/` of each match, so the next dot-segment in a chained sequence was left unescaped:

| Input                | Output (before fix)                      | Expected                            |
| -------------------- | ---------------------------------------- | ----------------------------------- |
| `/../../../`         | `/%2E%2E/../%2E%2E/`                     | `/%2E%2E/%2E%2E/%2E%2E/`            |
| `/foo/../../../bar`  | `/foo/%2E%2E/../%2E%2E/bar`              | `/foo/%2E%2E/%2E%2E/%2E%2E/bar`     |

When a route exposes a parameter constrained by a permissive requirement (`.+`, `.*`, or similar) that accepts dots and slashes, attacker-controlled chained `..` or `.` segments produce a generated URL that, under strict RFC 3986 normalization, collapses to a different path than the originating route. The Twig `path()` / `url()` helpers and any server-side use of `UrlGenerator` are affected. Same class of route round-trip integrity issue as CVE-2026-45065.

Note: WHATWG-conformant browsers treat `%2E`/`%2E%2E` as dot-segments during URL parsing, so the encoding never protected browser-side traversal. The defense exists for RFC-3986-conformant consumers; restoring it for chained segments closes the gap there.

### Resolution

`UrlGenerator` now matches every `/.` or `/..` dot-segment in a single left-to-right `preg_replace_callback` pass using a lookahead that does not consume the trailing `/`, so adjacent dot-segments are encoded correctly.

The patches for this issue are available [here](https://github.com/symfony/symfony/commit/4b63c3a3f7af04ecd79c89a594b0b02a01990b1d) for branch 5.4 (and forward-ported to 6.4, 7.4, 8.0 and 8.1).

### Credits

Symfony would like to thank Alex Pott for reporting the issue and Nicolas Grekas for providing the fix.

## References
- https://github.com/symfony/symfony/security/advisories/GHSA-h5x3-xfc9-m39h
- https://github.com/symfony/symfony/commit/4b63c3a3f7af04ecd79c89a594b0b02a01990b1d
- https://github.com/FriendsOfPHP/security-advisories/blob/master/symfony/routing/CVE-2026-48784.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/symfony/symfony/CVE-2026-48784.yaml
- https://github.com/symfony/symfony
- https://symfony.com/cve-2026-48784
