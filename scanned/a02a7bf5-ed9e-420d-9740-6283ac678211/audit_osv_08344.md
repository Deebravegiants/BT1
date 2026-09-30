# [H] CVE-2016-2347

## Summary
Severity: High
Advisory: CVE-2016-2347
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-04-21
Source: https://osv.dev/vulnerability/CVE-2016-2347
Type: osv

## Details
Integer underflow in the decode_level3_header function in lib/lha_file_header.c in Lhasa before 0.3.1 allows remote attackers to execute arbitrary code via a crafted archive.

## References
- http://lists.opensuse.org/opensuse-updates/2016-04/msg00038.html
- http://lists.opensuse.org/opensuse-updates/2016-04/msg00039.html
- http://www.debian.org/security/2016/dsa-3540
- https://github.com/fragglet/lhasa/commit/6fcdb8f1f538b9d63e63a5fa199c5514a15d4564
- https://github.com/fragglet/lhasa/releases/tag/v0.3.1
- http://www.talosintelligence.com/reports/TALOS-2016-0095/
