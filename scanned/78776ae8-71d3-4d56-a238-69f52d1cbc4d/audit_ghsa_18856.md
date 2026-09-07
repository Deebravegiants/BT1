# [M] python-ldap has sanitization bypass in ldap.filter.escape_filter_chars

## Summary
Severity: Medium
Advisory: GHSA-r7r6-cc7p-4v5m
CVE: CVE-2025-61911
CWE: CWE-75, CWE-843
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:L/VI:L/VA:N/SC:N/SI:N/SA:N/E:P (CVSS_V4)
Published: 2025-10-10
Source: https://github.com/advisories/GHSA-r7r6-cc7p-4v5m
Type: github-advisory

## Affected
- PyPI: `python-ldap` — affected >=0 <3.4.5

## Details
### Summary
The sanitization method `ldap.filter.escape_filter_chars` can be tricked to skip escaping of special characters when a crafted `list` or `dict` is supplied as the `assertion_value` parameter, and the non-default `escape_mode=1` is configured.

### Details
The method `ldap.filter.escape_filter_chars` supports 3 different escaping modes. `escape_mode=0` (default) and `escape_mode=2` happen to raise exceptions when a `list` or `dict` object is supplied as the `assertion_value` parameter. However, `escape_mode=1` happily computes without performing adequate logic to ensure a fully escaped return value.

### PoC
```
>>> import ldap.filter
```
**Exploitable**
```
>>> ldap.filter.escape_filter_chars(["abc@*()/xyz"], escape_mode=1)
'abc@*()/xyz'
>>> ldap.filter.escape_filter_chars({"abc@*()/xyz": 1}, escape_mode=1)
'abc@*()/xyz'
```
**Not exploitable**
```
>>> ldap.filter.escape_filter_chars("abc@*()/xyz", escape_mode=1)
'abc@\\2a\\28\\29\\2fxyz'
>>> ldap.filter.escape_filter_chars(["abc@*()/xyz"], escape_mode=0)
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "/usr/local/lib64/python3.12/site-packages/ldap/filter.py", line 41, in escape_filter_chars
    s = assertion_value.replace('\\', r'\5c')
        ^^^^^^^^^^^^^^^^^^^^^^^
AttributeError: 'list' object has no attribute 'replace'
>>> ldap.filter.escape_filter_chars(["abc@*()/xyz"], escape_mode=2)
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "/usr/local/lib64/python3.12/site-packages/ldap/filter.py", line 36, in escape_filter_chars
    r.append("\\%02x" % ord(c))
                        ^^^^^^
TypeError: ord() expected a character, but string of length 11 found
```
### Impact
If an application relies on the vulnerable method in the `python-ldap` library to escape untrusted user input, an attacker might be able to abuse the vulnerability to launch ldap injection attacks which could potentially disclose or manipulate ldap data meant to be inaccessible to them.

With Python being a dynamically typed language, and the commonly used `JSON` format supporting `list` and `dict`, it is to be expected that Python applications may commonly forward unchecked and potentially malicious `list` and `dict` objects to the vulnerable sanitization method.

The vulnerable `escape_mode=1` configuration does not appear to be widely used.

### Suggested Fix
Add a type check at the start of the `ldap.filter.escape_filter_chars` method to raise an exception when the supplied `assertion_value` parameter is not of type `str`.

## References
- https://github.com/python-ldap/python-ldap/security/advisories/GHSA-r7r6-cc7p-4v5m
- https://nvd.nist.gov/vuln/detail/CVE-2025-61911
- https://github.com/python-ldap/python-ldap/commit/3957526fb1852e84b90f423d9fef34c7af25b85a
- https://github.com/python-ldap/python-ldap
- https://github.com/python-ldap/python-ldap/releases/tag/python-ldap-3.4.5
