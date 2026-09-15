# [H] PHPMailer susceptible to arbitrary code execution

## Summary
Severity: High
Advisory: GHSA-v5c9-mmw9-829q
CVE: CVE-2008-5619
CWE: CWE-94
Ecosystem: Packagist
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-v5c9-mmw9-829q
Type: github-advisory

## Affected
- Packagist: `phpmailer/phpmailer` — affected >=0 <5.2.10

## Details
html2text.php in Chuggnutt HTML to Text Converter, as used in PHPMailer before 5.2.10, RoundCube Webmail (roundcubemail) 0.2-1.alpha and 0.2-3.beta, Mahara, and AtMail Open 1.03, allows remote attackers to execute arbitrary code via crafted input that is processed by the preg_replace function with the eval switch.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2008-5619
- https://github.com/PHPMailer/PHPMailer/commit/8beacc646acb67c995aea10ac5585970efc7355a
- https://github.com/PHPMailer/PHPMailer
- https://www.exploit-db.com/exploits/7549
- https://www.exploit-db.com/exploits/7553
- https://www.redhat.com/archives/fedora-package-announce/2008-December/msg00783.html
- https://www.redhat.com/archives/fedora-package-announce/2008-December/msg00802.html
- http://mahara.org/interaction/forum/topic.php?id=533
- http://osvdb.org/53893
- http://sourceforge.net/forum/forum.php?forum_id=898542
- http://trac.roundcube.net/changeset/2148
- http://trac.roundcube.net/ticket/1485618
- http://www.openwall.com/lists/oss-security/2008/12/12/1
