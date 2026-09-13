# [M] liferea Feed Enrichment update.c update_job_run os command injection

## Summary
Severity: Medium
Advisory: CVE-2023-1350
CVSS: 6.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L)
Published: 2023-03-11
Source: https://osv.dev/vulnerability/CVE-2023-1350
Type: osv

## Details
A vulnerability was found in liferea. It has been rated as critical. Affected by this issue is the function update_job_run of the file src/update.c of the component Feed Enrichment. The manipulation of the argument source with the input |date &gt;/tmp/bad-item-link.txt leads to os command injection. The attack may be launched remotely. The exploit has been disclosed to the public and may be used. The name of the patch is 8d8b5b963fa64c7a2122d1bbfbb0bed46e813e59. It is recommended to apply a patch to fix this issue. The identifier of this vulnerability is VDB-222848.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/1xxx/CVE-2023-1350.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-1350
- https://vuldb.com/?id.222848
- https://vuldb.com/?ctiid.222848
- https://github.com/lwindolf/liferea/commit/8d8b5b963fa64c7a2122d1bbfbb0bed46e813e59
