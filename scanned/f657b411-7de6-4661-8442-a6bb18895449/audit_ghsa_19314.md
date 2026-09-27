# [H] Django-Select2 Vulnerable to Widget Instance Secret Cache Key Leaking

## Summary
Severity: High
Advisory: GHSA-wjrh-hj83-3wh7
CVE: CVE-2025-48383
CWE: CWE-402, CWE-918
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2025-05-27
Source: https://github.com/advisories/GHSA-wjrh-hj83-3wh7
Type: github-advisory

## Affected
- PyPI: `django-select2` — affected >=0 <8.4.1

## Details
### Impact

Instances of `HeavySelect2Mixin` subclasses like the `ModelSelect2MultipleWidget` and `ModelSelect2Widget` can secret access tokens across requests. This can allow users to access restricted querysets and restricted data.

### Patches

The problem has been patched in version 8.4.1 and all following versions.

### Workarounds

This vulnerability is limited use cases where instances of widget classes are created during app loading (not during a request).

Example of affected code:
```python
class MyForm(forms.ModelForm):
    class Meta:
        widgets = {"my_select_field": Select2ModelWidget()}
```

Django allows you to pass just the widget class (not the instance). This can be used to mitigate the session request leak.

Example of affected code:
```python
class MyForm(forms.ModelForm):
    class Meta:
        widgets = {"my_select_field": Select2ModelWidget}
```



### References

Thanks to @neartik for reporting this issue. I will address it later. I had to delete your issue, to avoid exploitation of this security issue.

## References
- https://github.com/codingjoe/django-select2/security/advisories/GHSA-wjrh-hj83-3wh7
- https://nvd.nist.gov/vuln/detail/CVE-2025-48383
- https://github.com/codingjoe/django-select2/commit/e5f41e6edba004d35f94915ff5e2559f44853412
- https://github.com/codingjoe/django-select2
