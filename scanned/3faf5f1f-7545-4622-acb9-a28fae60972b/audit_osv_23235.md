# [M] CVE-2022-45873

## Summary
Severity: Medium
Advisory: CVE-2022-45873
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-11-23
Source: https://osv.dev/vulnerability/CVE-2022-45873
Type: osv

## Details
systemd 250 and 251 allows local users to achieve a systemd-coredump deadlock by triggering a crash that has a long backtrace. This occurs in parse_elf_object in shared/elf-util.c. The exploitation methodology is to crash a binary calling the same function recursively, and put it in a deeply nested directory to make its backtrace large enough to cause the deadlock. This must be done 16 times when MaxConnections=16 is set for the systemd/units/systemd-coredump.socket file.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/45xxx/CVE-2022-45873.json
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/MS5N5SLYAHKENLAJWYBDKU55ICU3SVZF/
- https://nvd.nist.gov/vuln/detail/CVE-2022-45873
- https://github.com/systemd/systemd/commit/076b807be472630692c5348c60d0c2b7b28ad437
- https://github.com/systemd/systemd/pull/24853#issuecomment-1326561497
- https://github.com/systemd/systemd/pull/25055#issuecomment-1313733553
