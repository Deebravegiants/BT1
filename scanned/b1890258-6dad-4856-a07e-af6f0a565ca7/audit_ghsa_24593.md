# [H] MantisBT allows arbitrary password reset

## Summary
Severity: High
Advisory: GHSA-252r-f55f-ff34
CVE: CVE-2017-7615
CWE: CWE-640
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-252r-f55f-ff34
Type: github-advisory

## Affected
- Packagist: `mantisbt/mantisbt` — affected >=1.3.0-rc.2 <1.3.10
- Packagist: `mantisbt/mantisbt` — affected >=2.0.0 <2.2.4
- Packagist: `mantisbt/mantisbt` — affected >=2.3.0 <2.3.1

## Details
MantisBT through 2.3.0 allows arbitrary password reset and unauthenticated admin access via an empty confirm_hash value to verify.php.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-7615
- https://github.com/mantisbt/mantisbt
- https://mantisbt.org/bugs/view.php?id=22690
- https://www.exploit-db.com/exploits/41890
- http://hyp3rlinx.altervista.org/advisories/MANTIS-BUG-TRACKER-PRE-AUTH-REMOTE-PASSWORD-RESET.txt
- http://packetstormsecurity.com/files/159219/Mantis-Bug-Tracker-2.3.0-Remote-Code-Execution.html
- http://www.openwall.com/lists/oss-security/2017/04/16/2
- http://www.securityfocus.com/bid/97707
