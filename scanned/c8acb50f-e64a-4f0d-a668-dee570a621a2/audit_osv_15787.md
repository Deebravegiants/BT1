# [H] CVE-2019-19648

## Summary
Severity: High
Advisory: CVE-2019-19648
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2019-12-09
Source: https://osv.dev/vulnerability/CVE-2019-19648
Type: osv

## Details
In the macho_parse_file functionality in macho/macho.c of YARA 3.11.0, command_size may be inconsistent with the real size. A specially crafted MachO file can cause an out-of-bounds memory access, resulting in Denial of Service (application crash) or potential code execution.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/FKNXSH5ERG6NELTXCYVJLUPJJJ2TNEBD/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/XXM224OLGI6KAOROLDPPGGCZ2OQVQ6HH/
- https://github.com/VirusTotal/yara/issues/1178
