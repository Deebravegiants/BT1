# [M] automad FileController.php import server-side request forgery

## Summary
Severity: Medium
Advisory: CVE-2023-7037
Aliases: GHSA-q5q3-qm26-9jwm
CVSS: 6.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L)
Published: 2023-12-21
Source: https://osv.dev/vulnerability/CVE-2023-7037
Type: osv

## Details
A vulnerability was found in automad up to 1.10.9. It has been declared as critical. This vulnerability affects the function import of the file FileController.php. The manipulation of the argument importUrl leads to server-side request forgery. The attack can be initiated remotely. The exploit has been disclosed to the public and may be used. VDB-248686 is the identifier assigned to this vulnerability. NOTE: The vendor was contacted early about this disclosure but did not respond in any way.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/7xxx/CVE-2023-7037.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-7037
- https://vuldb.com/?id.248686
- https://vuldb.com/?ctiid.248686
- https://github.com/screetsec/VDD/tree/main/Automad%20CMS/Authenticated%20Blind%20SSRF
