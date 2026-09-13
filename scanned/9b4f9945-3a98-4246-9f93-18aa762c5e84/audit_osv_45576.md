# [M] scp in OpenSSH before 10.4 may place a file in the parent directory of an intended directory when...

## Summary
Severity: Medium
Advisory: JLSEC-2026-1320
Ecosystem: Julia
CVSS: 5.4 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:L)
Published: 2026-08-14
Source: https://osv.dev/vulnerability/JLSEC-2026-1320
Type: osv

## Affected
- Julia: `OpenSSH_jll` — affected >=0 <10.4.1+0

## Details
scp in OpenSSH before 10.4 may place a file in the parent directory of an intended directory when the copy occurs between two remote destinations.

## References
- https://github.com/advisories/GHSA-8v2x-fhq9-4fv3
- https://marc.info/?l=openssh-unix-dev&m=178333966933090&w=2
- https://nvd.nist.gov/vuln/detail/CVE-2026-59996
- https://www.openssh.org/releasenotes.html#10.4p1
- https://www.openwall.com/lists/oss-security/2026/07/06/5
