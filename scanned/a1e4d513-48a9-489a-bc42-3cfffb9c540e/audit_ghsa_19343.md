# [M] Bootstrap Multiselect Vulnerable to CSRF and Reflective XSS via Arbitrary POST Data

## Summary
Severity: Medium
Advisory: GHSA-gv5r-9gxr-v74w
CVE: CVE-2025-47204
CWE: CWE-352, CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2025-05-13
Source: https://github.com/advisories/GHSA-gv5r-9gxr-v74w
Type: github-advisory

## Affected
- npm: `bootstrap-multiselect` — affected >=0 <2.0.0

## Details
An issue was discovered in post.php in bootstrap-multiselect (aka Bootstrap Multiselect) 1.1.2. A PHP script in the source code echoes arbitrary POST data. If a developer adopts this structure wholesale in a live application, it could create a Reflective Cross-Site Scripting (XSS) vulnerability exploitable through Cross-Site Request Forgery (CSRF).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-47204
- https://github.com/davidstutz/bootstrap-multiselect/issues/1286
- https://github.com/davidstutz/bootstrap-multiselect/pull/1287
- https://github.com/davidstutz/bootstrap-multiselect/commit/7da45ded9c82837a8eae9cb9dd3bd32a3dd1dc45
- https://github.com/projectdiscovery/nuclei-templates/commit/11e1a6c11d3954f44acfb0274b6dad4bd8045103
- https://github.com/davidstutz/bootstrap-multiselect
- https://github.com/davidstutz/bootstrap-multiselect/releases
