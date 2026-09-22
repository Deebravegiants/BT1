# [M] xml2rfc has file inclusion irregularities

## Summary
Severity: Medium
Advisory: GHSA-432c-wxpg-m4q3
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:L/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-02-07
Source: https://github.com/advisories/GHSA-432c-wxpg-m4q3
Type: github-advisory

## Affected
- PyPI: `xml2rfc` — affected >=3.12.0 <3.27.0

## Details
Version [3.12.0](https://github.com/ietf-tools/xml2rfc/blob/main/CHANGELOG.md#3120---2021-12-08) changed `xml2rfc` so that it would not access local files without the presence of its new `--allow-local-file-access` flag.
This prevented XML External Entity (XXE) injection attacks with `xinclude` and XML entity references.

It was discovered that `xml2rfc` does not respect `--allow-local-file-access` when a local file is specified as `src` in `artwork` or `sourcecode` elements. Furthermore, XML entity references can include any file inside the source dir and below without using the `--allow-local-file-access` flag. 

The `xml2rfc <= 3.26.0` behaviour:

|  | `xinclude` | XML entity reference | `artwork src=` | `sourcecode src=` |
|---|---|---|---|---|
| without `--allow-local-file-access` flag | No filesystem access | Any file in xml2rfc templates dir and below, any file in source directory and below | Access source directory and below | Access source directory and below |
| with `--allow-local-file-access` flag | Access any file on filesystem[^1] | Access any file on filesystem[^1] | Access source directory and below | Access source directory and below | Access source directory and below |

  [^1]: Access any file of the filesystem with the permissions of the user running `xml2rfc` can access.

### Impact

Anyone running `xml2rfc` as a service that accepts input from external users is impacted by this issue.
Specifying a file in `src` attribute in `artwork` or `sourcecode` elements will cause the contents of that file to appear in xml2rfc’s output results.
But that file has to be inside the same directory as the XML input source file.
For `artwork` and `sourcecode`, `xml2rfc` will not look above the source file directory.

### The proposed new behaviour
- Generalize file access checks.
- Only allow access to files within src dir and below. (xml entity include can access templates dir).
- Always allow access to `templates_dir` for XML entity includes.

New behaviour:

|  | `xinclude` | XML entity reference | `artwork src=` | `sourcecode src=` |
|---|---|---|---|---|
| without `--allow-local-file-access` flag | No filesystem access | No filesystem access _(except for `templates_dir`)_ | No filesystem access | No filesystem access |
| with `--allow-local-file-access` flag | Access source directory and below | Access source directory and below _(Can access`templates_dir`)._ | Access source directory and below | Access source directory and below |

### Workarounds

Use a secure temporary directory to process un-trusted XML files, and do not reuse it for processing other XML documents.

## References
- https://github.com/ietf-tools/xml2rfc/security/advisories/GHSA-432c-wxpg-m4q3
- https://github.com/ietf-tools/xml2rfc/commit/ec98f9cb4b9a8658222117df037dda473ca3f4e4
- https://github.com/ietf-tools/xml2rfc
