# [H] Sandbox escape via various forms of "format".

## Summary
Severity: High
Advisory: GHSA-xjw2-6jm9-rf67
CVE: CVE-2023-41039
CWE: CWE-74
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:C/C:H/I:H/A:L (CVSS_V3)
Published: 2023-08-30
Source: https://github.com/advisories/GHSA-xjw2-6jm9-rf67
Type: github-advisory

## Affected
- PyPI: `RestrictedPython` — affected >=0 <5.4
- PyPI: `RestrictedPython` — affected >=6.0 <6.2

## Details
### Impact
Python's "format" functionality allows someone controlling the format string to "read" all objects accessible through recursive attribute lookup and subscription from objects he can access. This can lead to critical information disclosure.
With `RestrictedPython`, the format functionality is available via the `format` and `format_map` methods of `str` (and `unicode`) (accessed either via the class or its instances) and via `string.Formatter`.
All known versions of `RestrictedPython` are vulnerable. 

### Patches
The issue will be fixed in 5.4 and 6.2.

### Workarounds
There are no workarounds to fix the issue without upgrading.

### References
* https://docs.python.org/3/library/stdtypes.html#str.format_map
* http://lucumr.pocoo.org/2016/12/29/careful-with-str-format/
* https://www.exploit-db.com/exploits/51580

### For more information

If you have any questions or comments about this advisory:

* Open an issue in the [RestrictedPython issue tracker](https://github.com/zopefoundation/RestrictedPython/issues)
* Email us at [security@plone.org](mailto:security@plone.org)

### Credits

Thanks for analysing and reporting the go to:

* Abhishek Govindarasu
* Ankush Menat
* Ward Theunisse

## References
- https://github.com/zopefoundation/RestrictedPython/security/advisories/GHSA-xjw2-6jm9-rf67
- https://nvd.nist.gov/vuln/detail/CVE-2023-41039
- https://github.com/zopefoundation/RestrictedPython/commit/4134aedcff17c977da7717693ed89ce56d54c120
- https://github.com/zopefoundation/RestrictedPython
