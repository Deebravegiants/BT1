# [M] EasyAdminBundle has path traversal and reflected XSS in Flag and Icon Twig components

## Summary
Severity: Medium
Advisory: GHSA-2wwr-9x6f-88gp
CWE: CWE-22, CWE-73, CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-07-01
Source: https://github.com/advisories/GHSA-2wwr-9x6f-88gp
Type: github-advisory

## Affected
- Packagist: `easycorp/easyadmin-bundle` — affected >=4.0.0 <4.29.10
- Packagist: `easycorp/easyadmin-bundle` — affected >=5.0.0 <5.0.10

## Details
EasyAdminBundle ships two public Twig components — `<twig:ea:Flag countryCode="...">` and `<twig:ea:Icon name="...">` — that load SVG files from disk using a path built directly from a public component property, and then render the resulting markup with the Twig `|raw` filter.

When an application binds either of those properties to data that is influenced by an end user, the lack of validation on the property value leads to two distinct issues:

- Arbitrary `.svg` file disclosure (both components) — the property value is concatenated into a filesystem path without normalizing or constraining it, so `..` segments are preserved and resolved by PHP. Any file on the server whose absolute path ends in `.svg` (for example, user-uploaded SVG icons stored elsewhere on the host) can be read and embedded into the rendered page.
- Reflected XSS in the admin UI (Flag component only) — when the requested flag file does not exist, the Flag component falls back to a hard-coded SVG string that interpolates the raw `countryCode` value twice, and the parent template renders that string with `|raw`. An attacker who controls `countryCode` can therefore inject arbitrary HTML/JavaScript that will execute inside the authenticated admin context that rendered the component.

The first-party usage shipped by EasyAdminBundle itself is not affected: the bundle only passes ISO 3166 alpha-2 codes validated through `Symfony\Component\Intl\Countries` to the `Flag` component, and only hard-coded `internal:..` names or values previously set in PHP via `MenuItem::setIcon()` to the `Icon` component. The vulnerability is reachable only in third-party templates that pass attacker-controlled data into these properties.

### Impact

Path traversal is information disclosure bounded by the `.svg` extension; reflected XSS in Flag runs in the admin context and is therefore more sensitive but requires a vulnerable template wiring and user interaction.

### Affected components

- `EasyCorp\Bundle\EasyAdminBundle\Twig\Component\Flag` — public Twig tag `<twig:ea:Flag>`, property `countryCode`.
- `EasyCorp\Bundle\EasyAdminBundle\Twig\Component\Icon` — public Twig tag `<twig:ea:Icon>`, property `name` when the value starts with the `internal:` prefix.

### Credit

EasyAdmin would like to thank Claude Mythos Preview (via Project Glasswing and The PHP Foundation) for reporting the issue and providing the fix.

## References
- https://github.com/EasyCorp/EasyAdminBundle/security/advisories/GHSA-2wwr-9x6f-88gp
- https://github.com/EasyCorp/EasyAdminBundle
