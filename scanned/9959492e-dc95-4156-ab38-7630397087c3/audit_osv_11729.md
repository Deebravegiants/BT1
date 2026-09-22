# [H] CVE-2017-9438

## Summary
Severity: High
Advisory: CVE-2017-9438
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-06-05
Source: https://osv.dev/vulnerability/CVE-2017-9438
Type: osv

## Details
libyara/re.c in the regexp module in YARA 3.5.0 allows remote attackers to cause a denial of service (stack consumption) via a crafted rule (involving hex strings) that is mishandled in the _yr_re_emit function, a different vulnerability than CVE-2017-9304.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/FKNXSH5ERG6NELTXCYVJLUPJJJ2TNEBD/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/XXM224OLGI6KAOROLDPPGGCZ2OQVQ6HH/
- https://github.com/VirusTotal/yara/commit/10e8bd3071677dd1fa76beeef4bc2fc427cea5e7
- https://github.com/VirusTotal/yara/issues/674
