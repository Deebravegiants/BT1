# [H] OpenCloud Reva has a Public Link Exploit

## Summary
Severity: High
Advisory: GHSA-9j2f-3rj3-wgpg
CVE: CVE-2026-23989
CWE: CWE-22, CWE-863
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2026-02-05
Source: https://github.com/advisories/GHSA-9j2f-3rj3-wgpg
Type: github-advisory

## Affected
- Go: `github.com/opencloud-eu/reva/v2` — affected >=0 <2.40.3
- Go: `github.com/opencloud-eu/reva/v2` — affected >=2.41.0 <2.42.3

## Details
### Impact

A security issue was discovered in Reva based products that enables a malicious user to bypass the scope validation of a public link, allowing it to access resources outside the scope of a public link.

### Details

Public link shares in OpenCloud are bound to a specific scope (usually a file or directory). Anonymous users accessing resources via this public link share are only allowed to access the share resource itself and, in case of a directory or space root, all child resources of it.

Due to a bug in the GRPC authorization middleware of the "Reva" component of OpenCloud a malicious user is able to bypass the scope verification. By exploiting this via the the "archiver" service this can be leveraged to create an archive (zip or tar-file) containing all resources that this creator of the public link has access to.

It is not possible to bypass the public link scope via "normal" WebDAV requests so it is not possible to exploit this vulnerability via WebDAV.

### Patches

Update to OpenCloud Reva version >= 2.40.3 for the 2.40.x versions.\
Update to OpenCloud Reva version >= 2.42.3 for the 2.41.x versions

### Workarounds

There is no workaround because one cannot run Reva standalone from this project. Please check the [OpenCloud Advisory](https://github.com/opencloud-eu/opencloud/security/advisories/GHSA-vf5j-r2hw-2hrw) how to mitigate the problem in an OpenCloud deployment via configuration.

### For more information

If there are any questions or comments about this advisory:

- Security Support: [security@opencloud.eu](mailto:security@opencloud.eu)
- Technical Support: [support@opencloud.eu](mailto:support@opencloud.eu)

## References
- https://github.com/opencloud-eu/reva/security/advisories/GHSA-9j2f-3rj3-wgpg
- https://nvd.nist.gov/vuln/detail/CVE-2026-23989
- https://github.com/opencloud-eu/reva/commit/95aa2bc5d980eaf6cc134d75782b4f5ac7b36ae1
- https://github.com/opencloud-eu/reva
