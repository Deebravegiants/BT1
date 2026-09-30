# [H] veraPDF has potential XSLT injection vulnerability when using policy files

## Summary
Severity: High
Advisory: GHSA-qxqf-2mfx-x8jw
CVE: CVE-2024-28109
CWE: CWE-91
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2024-05-20
Source: https://github.com/advisories/GHSA-qxqf-2mfx-x8jw
Type: github-advisory

## Affected
- Maven: `org.verapdf:core` — affected >=0 <1.24.2
- Maven: `org.verapdf:core-jakarta` — affected >=0 <1.24.2
- Maven: `org.verapdf:core-arlington` — affected >=0 <1.25.127
- Maven: `org.verapdf:verapdf-library-arlington` — affected >=0 <1.25.127
- Maven: `org.verapdf:verapdf-library` — affected >=0 <1.24.2
- Maven: `org.verapdf:verapdf-library-jakarta` — affected >=0 <1.24.2
- Maven: `org.verapdf:library-arlington` — affected >=0 <1.25.127
- Maven: `org.verapdf:library` — affected >=0 <1.24.2
- Maven: `org.verapdf:library-jakarta` — affected >=0 <1.24.2

## Details
### Impact

Executing policy checks using custom schematron files invokes an XSL transformation that may theoretically lead to a remote code execution (RCE) vulnerability.

### Patches

This has been patched and users should upgrade to veraPDF v1.24.2

### Workarounds

This doesn't affect the standard validation and policy checks functionality, veraPDF's common use cases. Most veraPDF users don't insert any custom XSLT code into policy profiles, which are based on Schematron syntax rather than direct XSL transforms. For users who do, only load custom policy files from sources you trust.

### References

Original issue: <https://github.com/veraPDF/veraPDF-library/issues/1415>

## References
- https://github.com/veraPDF/veraPDF-library/security/advisories/GHSA-qxqf-2mfx-x8jw
- https://nvd.nist.gov/vuln/detail/CVE-2024-28109
- https://github.com/veraPDF/veraPDF-library/issues/1415
- https://github.com/veraPDF/veraPDF-library/commit/614ffa477a2cf0819e4b0df1ab133610e0da25fb
- https://github.com/veraPDF/veraPDF-library/commit/9386ecbe1a1d1fb9e886d19df28851ed07890d9f
- https://github.com/veraPDF/veraPDF-library/commit/d5314cbdf4e058e0716f80dbdad2dbd8d96e6bfe
- https://github.com/veraPDF/veraPDF-library
