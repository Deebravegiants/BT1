# [H] changedetection.io path traversal using file URI scheme without supplying hostname

## Summary
Severity: High
Advisory: GHSA-6jrf-rcjf-245r
CVE: CVE-2024-51998
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2024-11-07
Source: https://github.com/advisories/GHSA-6jrf-rcjf-245r
Type: github-advisory

## Affected
- PyPI: `changedetection.io` — affected >=0 <0.47.6

## Details
### Summary

The validation for the file URI scheme falls short, and results in an attacker being able to read any file on the system. This issue only affects instances with a webdriver enabled, and `ALLOW_FILE_URI` false or not defined.

### Details

The check used for URL protocol, `is_safe_url`, allows `file:` as a URL scheme:

https://github.com/dgtlmoon/changedetection.io/blob/e0abf0b50507a8a3d0c1d8522ab23519b3e4cdf4/changedetectionio/model/Watch.py#L11-L13

It later checks if local files are permitted, but one of the preconditions for the check is that the URL starts with `file://`. The issue comes with the fact that the file URI scheme is not required to have double slashes.

> A valid file URI must therefore begin with either `file:/path` (no hostname), `file:///path` (empty hostname), or `file://hostname/path`.
> — [Wikipedia](https://en.wikipedia.org/wiki/File_URI_scheme#Number_of_slash_characters)

https://github.com/dgtlmoon/changedetection.io/blob/e0abf0b50507a8a3d0c1d8522ab23519b3e4cdf4/changedetectionio/processors/__init__.py#L37-L41

### PoC

1. Open up a changedetection.io instance with a webdriver configured
2. Create a new watch: `file:/etc/passwd` or a similar path for your operating system. Enable webdriver mode
3. Wait for it to be checked
4. Open preview
5. Notice contents of the file

## References
- https://github.com/dgtlmoon/changedetection.io/security/advisories/GHSA-6jrf-rcjf-245r
- https://nvd.nist.gov/vuln/detail/CVE-2024-51998
- https://github.com/dgtlmoon/changedetection.io/commit/49bc982c697169c98b79698889fb9d26f6b3317f
- https://github.com/dgtlmoon/changedetection.io
- https://github.com/dgtlmoon/changedetection.io/blob/e0abf0b50507a8a3d0c1d8522ab23519b3e4cdf4/changedetectionio/model/Watch.py#L11-L13
- https://github.com/dgtlmoon/changedetection.io/blob/e0abf0b50507a8a3d0c1d8522ab23519b3e4cdf4/changedetectionio/processors/__init__.py#L37-L41
- https://github.com/dgtlmoon/changedetection.io/releases/tag/0.47.06
