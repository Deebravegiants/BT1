# [H] MantisBT Host Header Injection vulnerability

## Summary
Severity: High
Advisory: GHSA-mcqj-7p29-9528
CVE: CVE-2024-23830
CWE: CWE-74
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:L (CVSS_V3)
Published: 2024-02-20
Source: https://github.com/advisories/GHSA-mcqj-7p29-9528
Type: github-advisory

## Affected
- Packagist: `mantisbt/mantisbt` — affected >=0 <2.26.1

## Details
### Impact
Knowing a user's email address and username, an unauthenticated attacker can hijack the user's account by poisoning the link in the password reset notification message.

### Patches
https://github.com/mantisbt/mantisbt/commit/7055731d09ff12b2781410a372f790172e279744

### Workarounds
Define `$g_path` as appropriate in config_inc.php.

### References
https://mantisbt.org/bugs/view.php?id=19381

### Credits

Thanks to the following security researchers for responsibly reporting and helping resolve this vulnerability.

- Pier-Luc Maltais (https://twitter.com/plmaltais) 
- Hlib Yavorskyi (https://github.com/Kerkroups)
- Jingshao Chen (https://github.com/shaozi)
- Brandon Roldan
- nhchoudhary

## References
- https://github.com/mantisbt/mantisbt/security/advisories/GHSA-mcqj-7p29-9528
- https://nvd.nist.gov/vuln/detail/CVE-2024-23830
- https://github.com/mantisbt/mantisbt/commit/7055731d09ff12b2781410a372f790172e279744
- https://github.com/mantisbt/mantisbt
- https://mantisbt.org/bugs/view.php?id=19381
