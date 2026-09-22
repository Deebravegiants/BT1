# [H] CVE-2026-37555

## Summary
Severity: High
Advisory: CVE-2026-37555
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-04-29
Source: https://osv.dev/vulnerability/CVE-2026-37555
Type: osv

## Details
An issue was discovered in libsndfile 1.2.2 IMA ADPCM codec. The AIFF code path (line 241) was fixed with (sf_count_t) cast, but the WAV code path (line 235) and close path (line 167) were not. When samplesperblock (int) * blocks (int) exceeds INT_MAX, the 32-bit multiplication overflows before being assigned to sf.frames (sf_count_t/int64). With samplesperblock=50000 and blocks=50000, the product 2500000000 overflows to -1794967296. This causes incorrect frame count leading to heap buffer overflow or denial of service. Both values come from the WAV file header and are attacker-controlled. This issue was discovered after an incomplete fix for CVE-2022-33065.

## References
- https://gist.github.com/sgInnora/a5f5c19e4bf6f4fb74fab7b0ef2bfcc1
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-37555.json
- https://access.redhat.com/errata/RHSA-2026:19559
- https://access.redhat.com/errata/RHSA-2026:19560
- https://access.redhat.com/errata/RHSA-2026:19610
- https://access.redhat.com/errata/RHSA-2026:23221
- https://access.redhat.com/errata/RHSA-2026:23222
- https://access.redhat.com/errata/RHSA-2026:23223
- https://access.redhat.com/errata/RHSA-2026:25092
- https://access.redhat.com/errata/RHSA-2026:25197
- https://access.redhat.com/errata/RHSA-2026:25198
- https://access.redhat.com/errata/RHSA-2026:25227
- https://access.redhat.com/errata/RHSA-2026:30078
- https://access.redhat.com/errata/RHSA-2026:30087
- https://access.redhat.com/errata/RHSA-2026:30088
- https://access.redhat.com/errata/RHSA-2026:30089
- https://access.redhat.com/security/cve/CVE-2026-37555
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/37xxx/CVE-2026-37555.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-37555
- https://bugzilla.redhat.com/show_bug.cgi?id=2463856
