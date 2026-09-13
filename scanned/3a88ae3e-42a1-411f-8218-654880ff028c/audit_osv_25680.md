# [M] CVE-2023-41710

## Summary
Severity: Medium
Advisory: CVE-2023-41710
CVSS: 5.4 (CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N)
Published: 2024-01-08
Source: https://osv.dev/vulnerability/CVE-2023-41710
Type: osv

## Details
User-defined script code could be stored for a upsell related shop URL. This code was not correctly sanitized when adding it to DOM. Attackers could lure victims to user accounts with malicious script code and make them execute it in the context of a trusted domain. We added sanitization for this content. No publicly available exploits are known.

## References
- http://seclists.org/fulldisclosure/2024/Jan/4
- https://documentation.open-xchange.com/appsuite/security/advisories/csaf/2023/oxas-adv-2023-0006.json
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/41xxx/CVE-2023-41710.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-41710
- https://software.open-xchange.com/products/appsuite/doc/Release_Notes_for_Patch_Release_6251_7.10.6_2023-09-25.pdf
