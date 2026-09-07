# [C] Command Injection in Pygments

## Summary
Severity: Critical
Advisory: GHSA-fff8-4w9p-7v76
CVE: CVE-2015-8557
CWE: CWE-78
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-fff8-4w9p-7v76
Type: github-advisory

## Affected
- PyPI: `Pygments` — affected >=1.2.2 <2.1

## Details
The FontManager._get_nix_font_path function in formatters/img.py in Pygments 1.2.2 through 2.0.2 allows remote attackers to execute arbitrary commands via shell metacharacters in a font name.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-8557
- https://github.com/pygments/pygments/commit/db6dd826f8624179e563aaded391efe824462f51
- https://bitbucket.org/birkenfeld/pygments-main/pull-requests/501/fix-shell-injection-in/diff
- https://github.com/advisories/GHSA-fff8-4w9p-7v76
- https://github.com/pygments/pygments
- https://github.com/pypa/advisory-database/tree/main/vulns/pygments/PYSEC-2016-32.yaml
- https://security.gentoo.org/glsa/201612-05
- http://packetstormsecurity.com/files/133823/Pygments-FontManager._get_nix_font_path-Shell-Injection.html
- http://seclists.org/fulldisclosure/2015/Oct/4
- http://www.debian.org/security/2016/dsa-3445
- http://www.openwall.com/lists/oss-security/2015/12/14/17
- http://www.openwall.com/lists/oss-security/2015/12/14/6
- http://www.oracle.com/technetwork/topics/security/bulletinjan2016-2867206.html
- http://www.ubuntu.com/usn/USN-2862-1
