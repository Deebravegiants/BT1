# [H] Paste Script has improper group memberships permissions

## Summary
Severity: High
Advisory: GHSA-27px-qpmj-qg38
CVE: CVE-2012-0878
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-27px-qpmj-qg38
Type: github-advisory

## Affected
- PyPI: `pastescript` — affected >=0 <2.0.1
- PyPI: `paste` — affected >=0 <1.7.5.1

## Details
Paste Script 1.7.5 and earlier does not properly set group memberships during execution with root privileges, which might allow remote attackers to bypass intended file-access restrictions by leveraging a web application that uses the local filesystem.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2012-0878
- https://github.com/cdent/pastescript/commit/b5f36f2995e1ae117cc53d2bd458d7fb33e4cabe
- https://bitbucket.org/ianb/pastescript/changeset/a19e462769b4
- https://bitbucket.org/ianb/pastescript/pull-request/3/fix-group-permissions-for-pastescriptserve
- https://bugzilla.redhat.com/show_bug.cgi?id=796790
- https://github.com/pasteorg/pastescript
- https://github.com/pypa/advisory-database/tree/main/vulns/paste/PYSEC-2012-15.yaml
- https://web.archive.org/web/20140723093519/http://secunia.com/advisories/50410
- https://web.archive.org/web/20140803132259/http://secunia.com/advisories/48812
- http://groups.google.com/group/paste-users/browse_thread/thread/2aa651ba331c2471
- http://rhn.redhat.com/errata/RHSA-2012-1206.html
- http://www.openwall.com/lists/oss-security/2012/02/23/1
- http://www.openwall.com/lists/oss-security/2012/02/23/4
