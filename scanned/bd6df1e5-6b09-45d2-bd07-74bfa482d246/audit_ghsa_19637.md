# [M] Solon Vulnerable to Path Traversal

## Summary
Severity: Medium
Advisory: GHSA-2m4q-2c6r-hmc3
CVE: CVE-2025-2961
CWE: CWE-23
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2025-03-31
Source: https://github.com/advisories/GHSA-2m4q-2c6r-hmc3
Type: github-advisory

## Affected
- Maven: `org.noear:solon-view` — affected >=0

## Details
A vulnerability classified as problematic was found in opensolon up to 3.1.0. This vulnerability affects the function render_mav of the file /aa of the component org.noear.solon.core.handle.RenderManager. The manipulation of the argument template with the input ../org/example/HelloApp.class leads to path traversal: '../filedir'. The attack can be initiated remotely. The exploit has been disclosed to the public and may be used.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-2961
- https://github.com/Q16G/cve_detail/blob/main/solon/templateRCE.md
- https://github.com/opensolon/solon
- https://vuldb.com/?ctiid.302014
- https://vuldb.com/?id.302014
- https://vuldb.com/?submit.522380
