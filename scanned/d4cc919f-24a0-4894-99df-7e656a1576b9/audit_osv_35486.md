# [M] CVE-2026-0394

## Summary
Severity: Medium
Advisory: CVE-2026-0394
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2026-03-27
Source: https://osv.dev/vulnerability/CVE-2026-0394
Type: osv

## Details
When dovecot has been configured to use per-domain passwd files, and they are placed one path component above /etc, or slash has been added to allowed characters, path traversal can happen if the domain component is directory partial. This allows inadvertently reading /etc/passwd (or some other path which ends with passwd). If this file contains passwords, it can be used to authenticate wrongly, or if this is userdb, it can unexpectly make system users appear valid users.  Upgrade to fixed version, or use different authentication scheme that does not rely on paths. Alternatively you can also ensure that the per-domain passwd files are in some other location, such as /etc/dovecot/auth/%d. No publicly available exploits are known.

## References
- https://documentation.open-xchange.com/dovecot/security/advisories/csaf/2026/oxdc-adv-2026-0001.json
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/0xxx/CVE-2026-0394.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-0394
