# [M] pyLoad open redirect vulnerability due to improper validation of the is_safe_url function

## Summary
Severity: Medium
Advisory: GHSA-g3cm-qg2v-2hj5
CVE: CVE-2024-24808
CWE: CWE-601
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2024-02-05
Source: https://github.com/advisories/GHSA-g3cm-qg2v-2hj5
Type: github-advisory

## Affected
- PyPI: `pyload-ng` — affected >=0 <0.5.0b3.dev79

## Details
### Summary
Open redirect vulnerability due to incorrect validation of input values when redirecting users after login.

### Details
pyload is validating URLs via the `get_redirect_url` function when redirecting users at login.
![301715649-f533db41-d0bd-44f7-8735-be1887fbd06c](https://github.com/pyload/pyload/assets/114328108/7fbec2ed-05ed-46e6-847f-05132cf3f136)


The URL entered in the `next` variable goes through the `is_safe_url` function, where a lack of validation can redirect the user to an arbitrary domain.
![301715667-2819b1d3-8a14-42f4-89c8-3d2fa84fc309](https://github.com/pyload/pyload/assets/114328108/613484f3-8097-4871-887d-8fa5eec817cc)


The documentation in the urllib library shows that improper URLs are recognized as relative paths when using the `urlparse` function. (https://docs.python.org/3/library/urllib.parse.html#urllib.parse.urlparse)

For example, When an unusual URL like `https:///example.com` is entered, `urlparse` interprets it as a relative path, but in the actual request it is converted to `https://example.com` due to url normalization.

### PoC
1. In the next variable, insert the URL to which you want to redirect the user.
![301715949-bb1451eb-5e84-451d-83b4-5c3e204d1df7](https://github.com/pyload/pyload/assets/114328108/6fe639ea-1f85-4715-bf6c-c9c8c4ee9c94)



2. Check that it is possible to bypass url validation and redirect users to an arbitrary url.
![301715824-3de6584a-878d-4ec4-a3d5-a34d11c6c0ac](https://github.com/pyload/pyload/assets/114328108/902b3244-a4ef-4f8e-8319-c4b92764f15f)
![301716107-ba5ab7b9-7aa8-4b7a-8924-eba82442b4c3](https://github.com/pyload/pyload/assets/114328108/35191d7b-50b9-4a46-8319-ebdebec20b41)



### Impact
An attacker can use this vulnerability to redirect users to malicious websites, which can be used for phishing and similar attacks.

## References
- https://github.com/pyload/pyload/security/advisories/GHSA-g3cm-qg2v-2hj5
- https://nvd.nist.gov/vuln/detail/CVE-2024-24808
- https://github.com/pyload/pyload/commit/fe94451dcc2be90b3889e2fd9d07b483c8a6dccd
- https://github.com/pyload/pyload
