# [M] OneDev: RCE through absolute-path symlink following allows low-privileged users to overwrite arbitrary server via TarUtils.untar

## Summary
Severity: Medium
Advisory: CVE-2026-49248
Aliases: GHSA-55g8-94r5-cj37
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:H/VA:N/SC:N/SI:H/SA:N)
Published: 2026-06-18
Source: https://osv.dev/vulnerability/CVE-2026-49248
Type: osv

## Details
OneDev is a Git server with CI/CD, kanban, and packages. In versions 15.0.6 and below, TarUtils.untar() creates symbolic links verbatim from TAR entry getLinkName() without validating whether the target is an absolute path. A subsequent file entry in the same archive traverses the symlink, writing to arbitrary server-side locations. This is exploitable by any authenticated user with CI Job write access — no admin interaction required. This is an incomplete fix bypass of CVE-2021-21251 (GHSA-2w6j-wc8c-9mq2): that patch blocked .. path segments but did not address absolute symlink targets. This issue has been fixed in version 15.0.7.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/49xxx/CVE-2026-49248.json
- https://github.com/theonedev/onedev/security/advisories/GHSA-55g8-94r5-cj37
- https://nvd.nist.gov/vuln/detail/CVE-2026-49248
- https://github.com/theonedev/onedev/commit/4f8684acebc4bfeefd3c7e23a34a4fd591cb27ad
