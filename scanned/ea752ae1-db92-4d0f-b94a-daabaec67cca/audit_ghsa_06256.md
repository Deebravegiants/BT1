# [H] Winter: Authenticated Twig sandbox escape in CMS SecurityPolicy (bypass of CVE-2024-54149)

## Summary
Severity: High
Advisory: GHSA-8cfw-pcwh-v63w
CWE: CWE-693
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-08-20
Source: https://github.com/advisories/GHSA-8cfw-pcwh-v63w
Type: github-advisory

## Affected
- Packagist: `winter/wn-system-module` — affected >=1.2.7 <1.2.13

## Details
### Impact

Affected versions of Winter CMS allow authenticated backend users with CMS template-editing permissions to escape the Twig sandbox ("safe mode") that is meant to restrict what template code can do. Using any of the following permissions, an attacker can read and modify arbitrary database records, execute arbitrary SQL (including DDL such as `DROP TABLE`), exfiltrate sensitive data such as backend administrator credentials, and achieve remote code execution by injecting PHP into a CMS page, layout, or partial code section:

- **`cms.manage_pages`**
- **`cms.manage_layouts`**
- **`cms.manage_partials`**

This is an incomplete-fix follow-up to CVE-2024-54149 (GHSA-xhw3-4j3m-hq53). That fix added a blocklist of dangerous methods to `System\Twig\SecurityPolicy`, but the blocklist missed a large number of equivalent methods and did not account for the way Eloquent models forward calls to the query builder. As a result the sandbox could be bypassed through — among others — `saveQuietly()`/`deleteQuietly()`, `increment()`/`decrement()`, `newQuery()`, `getConnection()`, `getConnectionResolver()`, relation and pivot methods, and higher-order collection methods that execute callables.

To actively exploit this issue, an attacker would need an authenticated backend account with one of the permissions listed above. These permissions are intended for trusted developers/administrators, and the sandbox is the additional protection layer this advisory is concerned with.

### Patches

`System\Twig\SecurityPolicy` has been reworked so that the blocklist reflects the real method-forwarding behaviour of the database layer rather than a flat list of method names. A method blocked on the query builder is now also blocked when it is reached through a model, Eloquent builder, or relation (via a transitive forwarder chain), which closes the `__call` forwarding escape that made the previous blocklist bypassable. In addition, the per-class blocklists have been expanded, the database connection and connection resolver are locked down, the `source()` and `constant()` Twig functions are restricted, and a `SafeCollection`/`SafePaginator` layer neutralises callable arguments passed to higher-order collection and paginator methods. Read-only query building continues to work as before; only data modification, raw SQL/connection access, and callable execution are blocked.

This security issue has been fixed in [v1.2.13](https://github.com/wintercms/winter/commit/725bbcda232466f7f71381c271c6916573d576e6).

After upgrading, clear the compiled Twig template cache (e.g. `php artisan cache:clear`) so that existing templates recompile under the updated policy.

### Workarounds

If you cannot upgrade immediately, apply https://github.com/wintercms/winter/commit/725bbcda232466f7f71381c271c6916573d576e6 manually. As an interim mitigation, restrict `cms.manage_pages`, `cms.manage_layouts`, and `cms.manage_partials` to fully trusted administrators only, since these permissions grant the ability to edit template code that the sandbox is designed to contain.

### References

- Original issue: CVE-2024-54149 / GHSA-xhw3-4j3m-hq53 — this advisory addresses an incomplete fix for it.

Credit to Mounir Elsrogy ([@M9nx](https://github.com/M9nx)) for reporting the issue.

### For more information

If you have any questions or comments about this advisory:
- Email us at [hello@wintercms.com](mailto:hello@wintercms.com)

## References
- https://github.com/wintercms/winter/security/advisories/GHSA-8cfw-pcwh-v63w
- https://github.com/wintercms/winter/commit/725bbcda232466f7f71381c271c6916573d576e6
- https://github.com/advisories/GHSA-xhw3-4j3m-hq53
- https://github.com/wintercms/winter
- https://github.com/wintercms/winter/releases/tag/v1.2.13
