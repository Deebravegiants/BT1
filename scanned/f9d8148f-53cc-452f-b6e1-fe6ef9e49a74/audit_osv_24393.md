# [M] Rebuild list queryListOfConfig sql injection

## Summary
Severity: Medium
Advisory: CVE-2023-1495
CVSS: 6.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L)
Published: 2023-03-18
Source: https://osv.dev/vulnerability/CVE-2023-1495
Type: osv

## Details
A vulnerability classified as critical was found in Rebuild up to 3.2.3. Affected by this vulnerability is the function queryListOfConfig of the file /admin/robot/approval/list. The manipulation of the argument q leads to sql injection. The attack can be launched remotely. The exploit has been disclosed to the public and may be used. The identifier of the patch is c9474f84e5f376dd2ade2078e3039961a9425da7. It is recommended to apply a patch to fix this issue. The identifier VDB-223381 was assigned to this vulnerability.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/1xxx/CVE-2023-1495.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-1495
- https://vuldb.com/?id.223381
- https://github.com/getrebuild/rebuild/issues/594
- https://vuldb.com/?ctiid.223381
- https://github.com/getrebuild/rebuild/commit/c9474f84e5f376dd2ade2078e3039961a9425da7
