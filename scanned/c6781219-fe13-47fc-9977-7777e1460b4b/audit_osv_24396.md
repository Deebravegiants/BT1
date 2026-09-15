# [M] DataGear pagingQueryData sql injection

## Summary
Severity: Medium
Advisory: CVE-2023-1571
CVSS: 6.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L)
Published: 2023-03-22
Source: https://osv.dev/vulnerability/CVE-2023-1571
Type: osv

## Details
A vulnerability, which was classified as critical, was found in DataGear up to 4.5.0. This affects an unknown part of the file /analysisProject/pagingQueryData. The manipulation of the argument queryOrder leads to sql injection. It is possible to initiate the attack remotely. The exploit has been disclosed to the public and may be used. Upgrading to version 4.5.1 is able to address this issue. It is recommended to upgrade the affected component. The associated identifier of this vulnerability is VDB-223563.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/1xxx/CVE-2023-1571.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-1571
- https://vuldb.com/?id.223563
- https://vuldb.com/?ctiid.223563
- https://github.com/yangyanglo/ForCVE/blob/main/2023-0x01.md
