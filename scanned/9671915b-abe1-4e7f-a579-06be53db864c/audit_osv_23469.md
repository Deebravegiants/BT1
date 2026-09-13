# [M] visegripped Stracker api.php getHistory sql injection

## Summary
Severity: Medium
Advisory: CVE-2022-4889
CVSS: 5.5 (CVSS:3.1/AV:A/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L)
Published: 2023-01-15
Source: https://osv.dev/vulnerability/CVE-2022-4889
Type: osv

## Details
A vulnerability classified as critical was found in visegripped Stracker. Affected by this vulnerability is the function getHistory of the file doc_root/public_html/stracker/api.php. The manipulation of the argument symbol/startDate/endDate leads to sql injection. The identifier of the patch is 63e1b040373ee5b6c7d1e165ecf5ae1603d29e0a. It is recommended to apply a patch to fix this issue. The identifier VDB-218377 was assigned to this vulnerability.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/4xxx/CVE-2022-4889.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-4889
- https://vuldb.com/?id.218377
- https://github.com/visegripped/stracker/pull/16
- https://vuldb.com/?ctiid.218377
- https://github.com/visegripped/stracker/commit/63e1b040373ee5b6c7d1e165ecf5ae1603d29e0a
