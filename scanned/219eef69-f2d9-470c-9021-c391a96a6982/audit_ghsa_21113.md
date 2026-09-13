# [H] Incorrect handling of invalid surrogate pair characters

## Summary
Severity: High
Advisory: GHSA-wpqr-jcpx-745r
CVE: CVE-2022-31116
CWE: CWE-670
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-07-05
Source: https://github.com/advisories/GHSA-wpqr-jcpx-745r
Type: github-advisory

## Affected
- PyPI: `ujson` — affected >=0 <5.4.0

## Details
### Impact
_What kind of vulnerability is it? Who is impacted?_

Anyone parsing JSON from an untrusted source is vulnerable.

JSON strings that contain escaped surrogate characters not part of a proper surrogate pair were decoded incorrectly. Besides corrupting strings, this allowed for potential key confusion and value overwriting in dictionaries.

Examples:

```python
# An unpaired high surrogate character is ignored.
>>> ujson.loads(r'"\uD800"')
''
>>> ujson.loads(r'"\uD800hello"')
'hello'

# An unpaired low surrogate character is preserved.
>>> ujson.loads(r'"\uDC00"')
'\udc00'

# A pair of surrogates with additional non surrogate characters pair up in spite of being invalid.
>>> ujson.loads(r'"\uD800foo bar\uDC00"')
'foo bar𐀀'
```

### Patches
_Has the problem been patched? What versions should users upgrade to?_

Users should upgrade to UltraJSON 5.4.0.

From version 5.4.0, UltraJSON decodes lone surrogates in the same way as the standard library's `json` module does, preserving them in the parsed output:

```python3
>>> ujson.loads(r'"\uD800"')
'\ud800'
>>> ujson.loads(r'"\uD800hello"')
'\ud800hello'
>>> ujson.loads(r'"\uDC00"')
'\udc00'
>>> ujson.loads(r'"\uD800foo bar\uDC00"')
'\ud800foo bar\udc00'
```

### Workarounds
_Is there a way for users to fix or remediate the vulnerability without upgrading?_

Short of switching to an entirely different JSON library, there are no safe alternatives to upgrading.

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [UltraJSON](http://github.com/ultrajson/ultrajson/issues)

## References
- https://github.com/ultrajson/ultrajson/security/advisories/GHSA-wpqr-jcpx-745r
- https://nvd.nist.gov/vuln/detail/CVE-2022-31116
- https://github.com/ultrajson/ultrajson/commit/67ec07183342589d602e0fcf7bb1ff3e19272687
- https://github.com/ultrajson/ultrajson
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/NAU5N4A7EUK2AMUCOLYDD5ARXAJYZBD2
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/OPPU5FZP3LCTXYORFH7NHUMYA5X66IA7
