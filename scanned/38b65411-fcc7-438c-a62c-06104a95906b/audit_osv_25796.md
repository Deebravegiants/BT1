# [M] OpenRapid RapidCMS run-movepass.php password recovery

## Summary
Severity: Medium
Advisory: CVE-2023-4448
CVSS: 6.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L)
Published: 2023-08-21
Source: https://osv.dev/vulnerability/CVE-2023-4448
Type: osv

## Details
A vulnerability was found in OpenRapid RapidCMS 1.3.1 and classified as critical. This issue affects some unknown processing of the file admin/run-movepass.php. The manipulation of the argument password/password2 leads to weak password recovery. The attack may be initiated remotely. The exploit has been disclosed to the public and may be used. The identifier of the patch is 4dff387283060961c362d50105ff8da8ea40bcbe. It is recommended to apply a patch to fix this issue. The identifier VDB-237569 was assigned to this vulnerability.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/4xxx/CVE-2023-4448.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-4448
- https://vuldb.com/?id.237569
- https://github.com/OpenRapid/rapidcms/issues/5
- https://vuldb.com/?ctiid.237569
- https://github.com/OpenRapid/rapidcms/commit/4dff387283060961c362d50105ff8da8ea40bcbe#diff-fc57d4c69cf5912c6edb5233c6df069a91106ebd481c115faf1ea124478b26d0
