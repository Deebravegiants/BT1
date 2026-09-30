# [M] CVE-2021-41792

## Summary
Severity: Medium
Advisory: CVE-2021-41792
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N)
Published: 2021-10-21
Source: https://osv.dev/vulnerability/CVE-2021-41792
Type: osv

## Details
An issue was discovered in Hyland org.alfresco:alfresco-content-services through 6.2.2.18 and org.alfresco:alfresco-transform-services through 1.3. A crafted HTML file, once uploaded, could trigger an unexpected request by the transformation engine. The response to the request is not available to the attacker, i.e., this is blind SSRF.

## References
- https://github.com/Alfresco/acs-packaging/blob/master/DISCLOSURES.md
- https://www.themissinglink.com.au/
