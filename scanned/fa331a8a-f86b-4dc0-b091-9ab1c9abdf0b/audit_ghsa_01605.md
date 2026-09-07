# [H] MoinMoin vulnerable to remote code execution via cache action

## Summary
Severity: High
Advisory: GHSA-52q8-877j-gghq
CVE: CVE-2020-25074
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2020-11-11
Source: https://github.com/advisories/GHSA-52q8-877j-gghq
Type: github-advisory

## Affected
- PyPI: `moin` — affected >=0 <1.9.11

## Details
### Impact
The cache action in action/cache.py allows directory traversal through a crafted HTTP request. An attacker who can upload attachments to the wiki can use this to achieve remote code execution.

### Patches
Users are strongly advised to upgrade to a patched version.

MoinMoin Wiki 1.9.11 has the necessary fixes and also contains other important fixes.

### Workarounds
It is not advised to work around this, but to upgrade MoinMoin to a patched version.

That said, a work around via disabling the `cache` or the `AttachFile` action might be possible.

Also, it is of course helpful if you give `write` permissions (which include uploading attachments) only to trusted users.

### Credits

This vulnerability was discovered by Michael Chapman.

### For more information
If you have any questions or comments about this advisory, email me at [twaldmann@thinkmo.de](mailto:twaldmann@thinkmo.de).

## References
- https://github.com/moinwiki/moin-1.9/security/advisories/GHSA-52q8-877j-gghq
- https://nvd.nist.gov/vuln/detail/CVE-2020-25074
- https://github.com/moinwiki/moin-1.9/commit/6b96a9060069302996b5af47fd4a388fc80172b7
- https://github.com/moinwiki/moin
- https://github.com/pypa/advisory-database/tree/main/vulns/moin/PYSEC-2020-67.yaml
- https://lists.debian.org/debian-lts-announce/2020/11/msg00020.html
- https://pypi.org/project/moin
- https://www.debian.org/security/2020/dsa-4787
- http://moinmo.in/SecurityFixes
