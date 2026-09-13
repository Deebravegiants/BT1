# [C] nterchange Code Injection vulnerability

## Summary
Severity: Critical
Advisory: GHSA-cp2p-6xh4-jmcp
CVE: CVE-2015-10009
CWE: CWE-94
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-01-02
Source: https://github.com/advisories/GHSA-cp2p-6xh4-jmcp
Type: github-advisory

## Affected
- Packagist: `nonfiction/nterchange` — affected >=0 <4.1.1

## Details
A vulnerability was found in nterchange up to 4.1.0. It has been rated as critical. This issue affects the function getContent of the file `app/controllers/code_caller_controller.php`. The manipulation of the argument q with the input %5C%27%29;phpinfo%28%29;/* leads to code injection. The exploit has been disclosed to the public and may be used. Upgrading to version 4.1.1 is able to address this issue. The name of the patch is fba7d89176fba8fe289edd58835fe45080797d99. It is recommended to upgrade the affected component. The associated identifier of this vulnerability is VDB-217187.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-10009
- https://github.com/nonfiction/nterchange_backend/commit/fba7d89176fba8fe289edd58835fe45080797d99
- https://github.com/nonfiction/nterchange_backend
- https://github.com/nonfiction/nterchange_backend/releases/tag/4.1.1
- https://vuldb.com/?ctiid.217187
- https://vuldb.com/?id.217187
