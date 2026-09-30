# [H] SQL injection in jackalope/jackalope-doctrine-dbal

## Summary
Severity: High
Advisory: GHSA-ph98-v78f-jqrm
CVE: CVE-2021-43822
CWE: CWE-89
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2021-12-14
Source: https://github.com/advisories/GHSA-ph98-v78f-jqrm
Type: github-advisory

## Affected
- Packagist: `jackalope/jackalope-doctrine-dbal` — affected >=0 <1.7.4

## Details
### Impact

Users can provoke SQL injections if they can specify a node name or query.

### Patches

Upgrade to version 1.7.4

If that is not possible, you can escape all places where `$property` is used to filter `sv:name` in the class `Jackalope\Transport\DoctrineDBAL\Query\QOMWalker`: `XPath::escape($property)`.

### Workarounds

Node names and xpaths can contain `"` or `;` according to the JCR specification. The jackalope component that translates the query object model into doctrine dbal queries does not properly escape the names and paths, so that a accordingly crafted node name can lead to an SQL injection.

If queries are never done from user input, or if you validate the user input to not contain `;`, you are not affected. 

### References

No further references.

### For more information

If you have any questions or comments about this advisory:

* Open an issue in [jackalope/jackalope-doctrine-dbal repo](https://github.com/jackalope/jackalope-doctrine-dbal/issues)

## References
- https://github.com/jackalope/jackalope-doctrine-dbal/security/advisories/GHSA-ph98-v78f-jqrm
- https://nvd.nist.gov/vuln/detail/CVE-2021-43822
- https://github.com/jackalope/jackalope-doctrine-dbal/commit/9d179a36d320330ddb303ea3a7c98d3a33d231db
- https://github.com/jackalope/jackalope-doctrine-dbal
