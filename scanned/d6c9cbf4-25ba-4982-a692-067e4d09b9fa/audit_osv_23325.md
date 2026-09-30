# [M] Dropbox merou SSH Public Key public_key.py add_public_key injection

## Summary
Severity: Medium
Advisory: CVE-2022-4768
CVSS: 6.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:L)
Published: 2022-12-27
Source: https://osv.dev/vulnerability/CVE-2022-4768
Type: osv

## Details
A vulnerability was found in Dropbox merou. It has been classified as critical. Affected is the function add_public_key of the file grouper/public_key.py of the component SSH Public Key Handler. The manipulation of the argument public_key_str leads to injection. It is possible to launch the attack remotely. The name of the patch is d93087973afa26bc0a2d0a5eb5c0fde748bdd107. It is recommended to apply a patch to fix this issue. VDB-216906 is the identifier assigned to this vulnerability.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/4xxx/CVE-2022-4768.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-4768
- https://vuldb.com/?id.216906
- https://github.com/dropbox/merou/pull/673
- https://vuldb.com/?ctiid.216906
- https://github.com/dropbox/merou/commit/d93087973afa26bc0a2d0a5eb5c0fde748bdd107
