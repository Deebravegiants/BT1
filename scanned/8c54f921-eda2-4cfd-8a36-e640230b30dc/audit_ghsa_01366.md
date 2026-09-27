# [H] Potential DoS with NumberFilter conversion to integer values.

## Summary
Severity: High
Advisory: GHSA-x7gm-rfgv-w973
CVE: CVE-2020-15225
CWE: CWE-681
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2020-09-28
Source: https://github.com/advisories/GHSA-x7gm-rfgv-w973
Type: github-advisory

## Affected
- PyPI: `django-filter` — affected >=0 <2.4.0

## Details
### Impact

Automatically generated `NumberFilter` instances, whose value was later converted to an integer, were subject to potential DoS from maliciously input using exponential format with sufficiently large exponents. 

### Patches

Version 2.4.0+ applies a `MaxValueValidator` with a a default `limit_value` of 1e50 to the form field used by `NumberFilter` instances. 

In addition, `NumberFilter` implements the new `get_max_validator()` which should return a configured validator instance to customise the limit, or else `None` to disable the additional validation. 

### Workarounds

Users may manually apply an equivalent validator if they are not able to upgrade.  

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [the django-filter repo](https://github.com/carltongibson/django-filter)

Thanks to Marcin Waraksa for the report.

## References
- https://github.com/carltongibson/django-filter/security/advisories/GHSA-x7gm-rfgv-w973
- https://nvd.nist.gov/vuln/detail/CVE-2020-15225
- https://github.com/carltongibson/django-filter/commit/340cf7a23a2b3dcd7183f6a0d6c383e85b130d2b
- https://github.com/carltongibson/django-filter
- https://github.com/carltongibson/django-filter/releases/tag/2.4.0
- https://github.com/pypa/advisory-database/tree/main/vulns/django-filter/PYSEC-2021-64.yaml
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/DPHENTRHRAYFXYPPBT7JRHZRWILRY44S
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/FAT2ZAEF6DM3VFSOHKB7X3ASSHGQHJAK
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/SVJ7AYU6FUSU3F653YCGW5LFD3IULRSX
- https://pypi.org/project/django-filter
- https://security.netapp.com/advisory/ntap-20210604-0010
