# [C] CVE-2022-44544

## Summary
Severity: Critical
Advisory: CVE-2022-44544
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-11-06
Source: https://osv.dev/vulnerability/CVE-2022-44544
Type: osv

## Details
Mahara 21.04 before 21.04.7, 21.10 before 21.10.5, 22.04 before 22.04.3, and 22.10 before 22.10.0 potentially allow a PDF export to trigger a remote shell if the site is running on Ubuntu and the flag -dSAFER is not set with Ghostscript.

## References
- https://bugs.launchpad.net/mahara/+bug/1979575
- https://mahara.org/interaction/forum/topic.php?id=9198
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/44xxx/CVE-2022-44544.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-44544
