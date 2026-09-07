# [C] OS Command Injection in ftpd

## Summary
Severity: Critical
Advisory: GHSA-7vxr-6cxg-j3x8
CVE: CVE-2013-2512
CWE: CWE-78
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-10-12
Source: https://github.com/advisories/GHSA-7vxr-6cxg-j3x8
Type: github-advisory

## Affected
- RubyGems: `ftpd` — affected >=0 <0.2.2

## Details
The ftpd gem 0.2.1 for Ruby allows remote attackers to execute arbitrary OS commands via shell metacharacters in a LIST or NLST command argument within FTP protocol traffic.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2013-2512
- https://github.com/wconrad/ftpd/commit/828064f1a0ab69b2642c59cab8292a67bb44182c
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/ftpd/CVE-2013-2512.yml
- https://github.com/wconrad/ftpd
- https://web.archive.org/web/20210206231123/http://vapidlabs.com/advisory.php?v=34
