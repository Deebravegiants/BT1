# [H] Gimp: gimp: heap buffer overflow in read_channel_data()

## Summary
Severity: High
Advisory: CVE-2026-58379
CVSS: 7.3 (CVSS:3.1/AV:L/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-07-03
Source: https://osv.dev/vulnerability/CVE-2026-58379
Type: osv

## Details
A flaw was found in GIMP's Paint Shop Pro (PSP) file format parser. This heap buffer overflow vulnerability allows a remote attacker to cause arbitrary code execution or a denial of service (DoS) by tricking a user into opening a specially crafted PSP image file. The vulnerability occurs because the software incorrectly calculates buffer sizes when processing low bit-depth images, leading to an overwrite of adjacent memory.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://access.redhat.com/errata/RHSA-2026:38496
- https://access.redhat.com/security/cve/CVE-2026-58379
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/58xxx/CVE-2026-58379.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-58379
- https://bugzilla.redhat.com/show_bug.cgi?id=2495997
- https://gitlab.gnome.org/GNOME/gimp/-/issues/16205
- https://gitlab.gnome.org/GNOME/gimp/-/commit/b630f167
