# [C] CVE-2021-3402

## Summary
Severity: Critical
Advisory: CVE-2021-3402
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2021-05-14
Source: https://osv.dev/vulnerability/CVE-2021-3402
Type: osv

## Details
An integer overflow and several buffer overflow reads in libyara/modules/macho/macho.c in YARA v4.0.3 and earlier could allow an attacker to either cause denial of service or information disclosure via a malicious Mach-O file. Affects all versions before libyara 4.0.4

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/FKNXSH5ERG6NELTXCYVJLUPJJJ2TNEBD/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/XXM224OLGI6KAOROLDPPGGCZ2OQVQ6HH/
- https://bugzilla.redhat.com/show_bug.cgi?id=1930175
- https://www.openwall.com/lists/oss-security/2021/01/29/2
- https://www.x41-dsec.de/lab/advisories/x41-2021-001-yara/
