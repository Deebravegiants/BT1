# [M] Formula Injection in Exported Data

## Summary
Severity: Medium
Advisory: GHSA-7rq4-qcpw-74gq
Ecosystem: PyPI
Published: 2022-06-17
Source: https://github.com/advisories/GHSA-7rq4-qcpw-74gq
Type: github-advisory

## Affected
- PyPI: `inventree` — affected >=0 <0.7.2

## Details
### Impact

Datasets exported to file (e.g. CSV / XLS) are not sufficiently sanitized, to neutralize potential formula injection

### Patches

- The issue is addressed in the upcoming 0.8.0 release
- This fix will also be back-ported to the 0.7.x branch, applied to the 0.7.2 release

### Workarounds

Users exporting untrusted data should open the files in safe mode (e.g. in Microsoft Excel).

### References

- https://huntr.dev/bounties/e57c36e7-fa39-435f-944a-3a52ee066f73/
- https://owasp.org/www-community/attacks/CSV_Injection

### For more information

If you have any questions or comments about this advisory:

* Open an issue in [github](http://github.com/inventree/inventree)
* Email us at [security@inventree.org](mailto:security@inventree.org)

## References
- https://github.com/inventree/InvenTree/security/advisories/GHSA-7rq4-qcpw-74gq
- https://github.com/inventree/inventree-python
