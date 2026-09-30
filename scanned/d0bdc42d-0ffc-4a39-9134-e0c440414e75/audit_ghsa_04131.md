# [H] Improper Input Validation python-gnupg

## Summary
Severity: High
Advisory: GHSA-2fch-jvg5-crf6
CVE: CVE-2019-6690
CWE: CWE-20
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2019-03-25
Source: https://github.com/advisories/GHSA-2fch-jvg5-crf6
Type: github-advisory

## Affected
- PyPI: `python-gnupg` — affected >=0 <0.4.4

## Details
python-gnupg 0.4.3 allows context-dependent attackers to trick gnupg to decrypt other ciphertext than intended. To perform the attack, the passphrase to gnupg must be controlled by the adversary and the ciphertext should be trusted. Related to a "CWE-20: Improper Input Validation" issue affecting the affect functionality component.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-6690
- https://blog.hackeriet.no/cve-2019-6690-python-gnupg-vulnerability
- https://github.com/advisories/GHSA-2fch-jvg5-crf6
- https://lists.debian.org/debian-lts-announce/2019/02/msg00021.html
- https://lists.debian.org/debian-lts-announce/2021/12/msg00027.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/3WMV6XNPPL3VB3RQRFFOBCJ3AGWC4K47
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/W6KYZMN2PWXY4ENZVJUVTGFBVYEVY7II
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/X4VFRUG56542LTYK4444TPJBGR57MT25
- https://pypi.org/project/python-gnupg/#history
- https://seclists.org/bugtraq/2019/Jan/41
- https://usn.ubuntu.com/3964-1
- https://web.archive.org/web/20200227091727/http://www.securityfocus.com/bid/106756
- http://lists.opensuse.org/opensuse-security-announce/2019-02/msg00008.html
- http://lists.opensuse.org/opensuse-security-announce/2019-02/msg00058.html
- http://packetstormsecurity.com/files/151341/Python-GnuPG-0.4.3-Improper-Input-Validation.html
