# [H] Insufficient HTML Sanitization

## Summary
Severity: High
Advisory: GHSA-rm89-9g65-4ffr
Ecosystem: PyPI
Published: 2022-06-17
Source: https://github.com/advisories/GHSA-rm89-9g65-4ffr
Type: github-advisory

## Affected
- PyPI: `inventree` — affected >=0 <0.7.2

## Details
### Impact

Affected versions can have malicious javascript code injected into the users browser by other authenticated users, as data fields retrieved from the database are not properly sanitized before displaying in various front-end views.

The problem here stems from multiple issues:

- Insufficient database sanitation on multiple fields allows injection of un-sanitized HTML
- Lack of HTML escaping when rendering data on the front end

The attack vector here is limited, as only authenticated users are able to write data to the database, for it to be subsequently rendered on the front-end. However, it is a vulnerability that the InvenTree development team takes seriously.

### Solution

The proposed patch for this vulnerability is prevents injection of un-escaped fields into front-end UI elements.

A future patch will also address sanitization of database fields on the "back end", however this will require a much larger effort to refactor multiple database tables.

### Patches

- The issue is addressed in the upcoming `0.8.0` release
- This fix will also be back-ported to the `0.7.x` branch, applied to the `0.7.2` release

### Workarounds

There are no workarounds for this issue, users should upgrade to a patched version.

### References

- https://huntr.dev/bounties/4cae8442-c042-43c2-ad89-6f666eaf3d57/
- https://huntr.dev/bounties/9d640ef2-c52c-4106-b043-f7497d577078/
- https://huntr.dev/bounties/b114e82f-6c02-485b-82ea-e242f89169c2/
- https://huntr.dev/bounties/22783cd3-1b2c-48fc-b31f-03b53c86da0b/

Thank you @saharshtapi for bringing this issue to our attention and giving pointers for fixing them.

### For more information

If you have any questions or comments about this advisory:

* Open an issue in [github](http://github.com/inventree/inventree)
* Email us at [security@inventree.org](mailto:security@inventree.org)

## References
- https://github.com/inventree/InvenTree/security/advisories/GHSA-rm89-9g65-4ffr
- https://github.com/inventree/inventree-python
