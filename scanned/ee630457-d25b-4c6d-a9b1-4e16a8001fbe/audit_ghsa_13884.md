# [H] MultipartParser denial of service with too many fields or files

## Summary
Severity: High
Advisory: GHSA-74m5-2c7w-9w3x
CVE: CVE-2023-30798
CWE: CWE-400
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-02-14
Source: https://github.com/advisories/GHSA-74m5-2c7w-9w3x
Type: github-advisory

## Affected
- PyPI: `starlette` — affected >=0 <0.25.0

## Details
### Impact

The `MultipartParser` using the package `python-multipart` accepts an unlimited number of multipart parts (form fields or files).

Processing too many parts results in high CPU usage and high memory usage, eventually leading to an <abbr title="out of memory">OOM</abbr> process kill.

This can be triggered by sending too many small form fields with no content, or too many empty files.

For this to take effect application code has to:

* Have `python-multipart` installed and
* call `request.form()`
  * or via another framework like FastAPI, using form field parameters or `UploadFile` parameters, which in turn calls `request.form()`.

### Patches

The vulnerability is solved in Starlette 0.25.0 by making the maximum fields and files customizable and with a sensible default (1000). 

Applications will be secure by just upgrading their Starlette version to 0.25.0 (or FastAPI to 0.92.0).

If application code needs to customize the new max field and file number, there are new `request.form()` parameters (with the default values):

* `max_files=1000`
* `max_fields=1000`

### Workarounds

Applications that don't install `python-multipart` or that don't use form fields are safe.

In older versions, it's also possible to instead of calling `request.form()` call `request.stream()` and parse the form data in internal code.

In most cases, the best solution is to upgrade the Starlette version.

### References

This was reported in private by @das7pad via internal email. He also coordinated the fix across multiple frameworks and parsers.

The details about how `multipart/form-data` is structured and parsed are in the [RFC 7578](https://www.rfc-editor.org/rfc/rfc7578).

## References
- https://github.com/encode/starlette/security/advisories/GHSA-74m5-2c7w-9w3x
- https://nvd.nist.gov/vuln/detail/CVE-2023-30798
- https://github.com/encode/starlette/commit/8c74c2c8dba7030154f8af18e016136bea1938fa
- https://github.com/encode/starlette
- https://github.com/pypa/advisory-database/tree/main/vulns/starlette/PYSEC-2023-48.yaml
- https://vulncheck.com/advisories/starlette-multipartparser-dos
