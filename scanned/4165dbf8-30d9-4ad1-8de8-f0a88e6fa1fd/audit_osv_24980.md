# [H] CVE-2023-29051

## Summary
Severity: High
Advisory: CVE-2023-29051
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N)
Published: 2024-01-08
Source: https://osv.dev/vulnerability/CVE-2023-29051
Type: osv

## Details
User-defined OXMF templates could be used to access a limited part of the internal OX App Suite Java API. The existing switch to disable the feature by default was not effective in this case. Unauthorized users could discover and modify application state, including objects related to other users and contexts. We now make sure that the switch to disable user-generated templates by default works as intended and will remove the feature in future generations of the product. No publicly available exploits are known.

## References
- http://seclists.org/fulldisclosure/2024/Jan/4
- https://documentation.open-xchange.com/appsuite/security/advisories/csaf/2023/oxas-adv-2023-0006.json
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/29xxx/CVE-2023-29051.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-29051
- https://software.open-xchange.com/products/appsuite/doc/Release_Notes_for_Patch_Release_6251_7.10.6_2023-09-25.pdf
