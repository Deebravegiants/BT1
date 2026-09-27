# [H] CVE-2026-60002

## Summary
Severity: High
Advisory: CVE-2026-60002
CVSS: 7.7 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:L)
Published: 2026-07-08
Source: https://osv.dev/vulnerability/CVE-2026-60002
Type: osv

## Details
ssh in OpenSSH before 10.4 can have a use-after-free when a server changes its host key during a key re-exchange. (This outcome occurs only on the client side.)

## References
- https://marc.info/?l=openssh-unix-dev&m=178333966933090&w=2
- https://www.openssh.org/releasenotes.html#10.4p1
- https://www.openwall.com/lists/oss-security/2026/07/06/5
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/60xxx/CVE-2026-60002.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-60002
