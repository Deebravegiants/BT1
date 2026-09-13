# [M] Mercurial Improper Certificate Validation vulnerability

## Summary
Severity: Medium
Advisory: GHSA-7gf7-7wx4-mxmw
CVE: CVE-2010-4237
CWE: CWE-295
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-04-21
Source: https://github.com/advisories/GHSA-7gf7-7wx4-mxmw
Type: github-advisory

## Affected
- PyPI: `mercurial` — affected >=0 <1.6.4

## Details
Mercurial before 1.6.4 fails to verify the Common Name field of SSL certificates which allows remote attackers who acquire a certificate signed by a Certificate Authority to perform a man-in-the-middle attack.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2010-4237
- https://github.com/dscho/hg/commit/4ea63fb25ceeeaaa4cd1026f733b7ea7672c30b3
- https://github.com/dscho/hg/commit/89baabf4fb7abf30ef6fdcf3d455a7893e5cc145
- https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=598841
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2010-4237
- https://bz.mercurial-scm.org/show_bug.cgi?id=2407
- https://repo.mercurial-scm.org/hg/rev/6ab4a7d3c179
- https://repo.mercurial-scm.org/hg/rev/f2937d6492c5
- https://security-tracker.debian.org/tracker/CVE-2010-4237
