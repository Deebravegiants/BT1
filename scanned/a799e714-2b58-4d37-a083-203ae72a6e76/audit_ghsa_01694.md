# [M] Pillow Temporary file name leakage

## Summary
Severity: Medium
Advisory: GHSA-r854-96gq-rfg3
CVE: CVE-2014-1933
CWE: CWE-200
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2020-05-18
Source: https://github.com/advisories/GHSA-r854-96gq-rfg3
Type: github-advisory

## Affected
- PyPI: `pillow` — affected >=0 <2.3.1

## Details
The (1) JpegImagePlugin.py and (2) EpsImagePlugin.py scripts in Python Image Library (PIL) 1.1.7 and earlier and Pillow before 2.3.1 uses the names of temporary files on the command line, which makes it easier for local users to conduct symlink attacks by listing the processes.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-1933
- https://github.com/python-imaging/Pillow/commit/4e9f367dfd3f04c8f5d23f7f759ec12782e10ee7
- https://github.com/pypa/advisory-database/tree/main/vulns/pillow/PYSEC-2014-23.yaml
- https://github.com/python-imaging/Pillow
- https://security.gentoo.org/glsa/201612-52
- http://lists.opensuse.org/opensuse-updates/2014-05/msg00002.html
- http://www.openwall.com/lists/oss-security/2014/02/10/15
- http://www.openwall.com/lists/oss-security/2014/02/11/1
- http://www.ubuntu.com/usn/USN-2168-1
