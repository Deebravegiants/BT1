# [M] 1Panel swap baseApi.UpdateDeviceSwap command injection

## Summary
Severity: Medium
Advisory: CVE-2024-2352
Aliases: GHSA-x2vg-5wrf-vj6v, GO-2024-2636
CVSS: 6.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L)
Published: 2024-03-10
Source: https://osv.dev/vulnerability/CVE-2024-2352
Type: osv

## Details
A vulnerability, which was classified as critical, has been found in 1Panel up to 1.10.1-lts. Affected by this issue is the function baseApi.UpdateDeviceSwap of the file /api/v1/toolbox/device/update/swap. The manipulation of the argument Path with the input 123123123\nopen -a Calculator leads to command injection. The attack may be launched remotely. The exploit has been disclosed to the public and may be used. It is recommended to apply a patch to fix this issue. The identifier of this vulnerability is VDB-256304.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/2xxx/CVE-2024-2352.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-2352
- https://vuldb.com/?id.256304
- https://github.com/1Panel-dev/1Panel/pull/4131
- https://github.com/1Panel-dev/1Panel/pull/4131#issue-2176105990
- https://vuldb.com/?ctiid.256304
- https://github.com/1Panel-dev/1Panel/pull/4131/commits/0edd7a9f6f5100aab98a0ea6e5deedff7700396c
