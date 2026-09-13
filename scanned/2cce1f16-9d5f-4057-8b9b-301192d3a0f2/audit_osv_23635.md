# [M] ualbertalib NEOSDiscovery _refworks.html.erb reverse tabnabbing

## Summary
Severity: Medium
Advisory: CVE-2022-4927
CVSS: 5.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:L/I:L/A:L)
Published: 2023-03-05
Source: https://osv.dev/vulnerability/CVE-2022-4927
Type: osv

## Details
A vulnerability was found in ualbertalib NEOSDiscovery 1.0.70 and classified as problematic. This issue affects some unknown processing of the file app/views/bookmarks/_refworks.html.erb. The manipulation leads to use of web link to untrusted target with window.opener access. The attack may be initiated remotely. Upgrading to version 1.0.71 is able to address this issue. The patch is named abe9f57123e0c278ae190cd7402a623d66c51375. It is recommended to upgrade the affected component. The associated identifier of this vulnerability is VDB-222287.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/4xxx/CVE-2022-4927.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-4927
- https://vuldb.com/?id.222287
- https://github.com/ualbertalib/NEOSDiscovery/pull/547
- https://vuldb.com/?ctiid.222287
- https://github.com/ualbertalib/NEOSDiscovery/commit/abe9f57123e0c278ae190cd7402a623d66c51375
- https://github.com/ualbertalib/NEOSDiscovery/releases/tag/1.0.71
