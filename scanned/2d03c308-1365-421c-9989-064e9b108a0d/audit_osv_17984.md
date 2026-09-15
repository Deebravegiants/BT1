# [H] CVE-2020-22219

## Summary
Severity: High
Advisory: CVE-2020-22219
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-08-22
Source: https://osv.dev/vulnerability/CVE-2020-22219
Type: osv

## Details
Buffer Overflow vulnerability in function bitwriter_grow_ in flac before 1.4.0 allows remote attackers to run arbitrary code via crafted input to the encoder.

## References
- https://lists.debian.org/debian-lts-announce/2023/09/msg00028.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/ZD2AJTU4PCJQP7HPTS2L2ELJWBASCRGD/
- https://www.debian.org/security/2023/dsa-5500
- https://github.com/xiph/flac/issues/215
