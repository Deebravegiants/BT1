# [M] Fabric vulnerable to symlink attack on tmp files

## Summary
Severity: Medium
Advisory: GHSA-xwg2-qc6c-7c3q
CVE: CVE-2011-2185
CWE: CWE-59
Ecosystem: PyPI
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-xwg2-qc6c-7c3q
Type: github-advisory

## Affected
- PyPI: `fabric` — affected >=0 <1.1.0

## Details
Fabric before 1.1.0 allows local users to overwrite arbitrary files via a symlink attack on (1) a `/tmp/fab.*.tar` file or (2) certain other files in the top level of `/tmp/`.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2011-2185
- https://github.com/fabric/fabric/commit/3445b5653cd297039443110548fb3cab2e8e25af
- https://github.com/fabric/fabric/commit/d7470d2db919ffcee80c245cf87e6d8d4ba6909c
- https://bugzilla.redhat.com/show_bug.cgi?id=710462
- https://github.com/fabric/fabric
- http://bugs.debian.org/cgi-bin/bugreport.cgi?bug=629003
- http://code.fabfile.org/projects/fabric/files/Fabric-1.1.0.tar.gz
- http://lists.fedoraproject.org/pipermail/package-announce/2011-July/062534.html
- http://www.openwall.com/lists/oss-security/2011/06/03/5
- http://www.openwall.com/lists/oss-security/2011/06/06/12
