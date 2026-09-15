# [H] PIL and Pillow Vulnerable to Symlink Attack on Tmpfiles

## Summary
Severity: High
Advisory: GHSA-x895-2wrm-hvp7
CVE: CVE-2014-1932
CWE: CWE-59
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-x895-2wrm-hvp7
Type: github-advisory

## Affected
- PyPI: `pillow` — affected >=0 <2.3.1

## Details
The (1) `load_djpeg` function in `JpegImagePlugin.py`, (2) `Ghostscript` function in `EpsImagePlugin.py`, (3) `load` function in `IptcImagePlugin.py`, and (4) `_copy` function in `Image.py` in Python Image Library (PIL) 1.1.7 and earlier and Pillow before 2.3.1 do not properly create temporary files, which allow local users to overwrite arbitrary files and obtain sensitive information via a symlink attack on the temporary file.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-1932
- https://github.com/python-imaging/Pillow/commit/4e9f367dfd3f04c8f5d23f7f759ec12782e10ee7
- https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=737059
- https://github.com/pypa/advisory-database/tree/main/vulns/pillow/PYSEC-2014-22.yaml
- https://github.com/python-pillow/Pillow
- https://security.gentoo.org/glsa/201612-52
- https://web.archive.org/web/20170103151725/http://www.securityfocus.com/bid/65511
- http://lists.opensuse.org/opensuse-updates/2014-05/msg00002.html
- http://www.openwall.com/lists/oss-security/2014/02/11/1
- http://www.ubuntu.com/usn/USN-2168-1
