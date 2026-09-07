# [H] Moodle XML import of ddwtos could lead to intentional remote code execution

## Summary
Severity: High
Advisory: GHSA-c3pr-h96w-2jjg
CVE: CVE-2018-14630
CWE: CWE-94
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-c3pr-h96w-2jjg
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=3.5.0 <3.5.2
- Packagist: `moodle/moodle` — affected >=3.4.0 <3.4.5
- Packagist: `moodle/moodle` — affected >=3.2.0 <3.3.8
- Packagist: `moodle/moodle` — affected >=0 <3.1.14

## Details
moodle before versions 3.5.2, 3.4.5, 3.3.8, 3.1.14 is vulnerable to an XML import of ddwtos could lead to intentional remote code execution. When importing legacy 'drag and drop into text' (ddwtos) type quiz questions, it was possible to inject and execute PHP code from within the imported questions, either intentionally or by importing questions from an untrusted source.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-14630
- https://github.com/moodle/moodle/commit/09cbca8566a388e8f0a1a0cfd86cd0667088ed2c
- https://github.com/moodle/moodle/commit/be092b730910ad97fff0511e177a097ec1cc4b1c
- https://github.com/moodle/moodle/commit/cb8aefa658cf7ad8f002a480343afb2dea94cc08
- https://github.com/moodle/moodle/commit/cfc4393aa689c277a27b9a040ff7dcbdac4e41dd
- https://github.com/moodle/moodle/commit/da1eeea0ff3d292b7669e478abc114872dd9cc8f
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2018-14630
- https://github.com/moodle/moodle
- https://moodle.org/mod/forum/discuss.php?d=376023
- https://seclists.org/fulldisclosure/2018/Sep/28
- https://web.archive.org/web/20200227111301/https://www.securityfocus.com/bid/105354
- https://www.sec-consult.com/en/blog/advisories/remote-code-execution-php-unserialize-moodle-open-source-learning-platform-cve-2018-14630
- http://git.moodle.org/gw?p=moodle.git&a=search&h=HEAD&st=commit&s=MDL-62880
