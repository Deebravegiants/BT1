# [M] JLSEC-2026-76

## Summary
Severity: Medium
Advisory: JLSEC-2026-76
Ecosystem: Julia
CVSS: 6.5 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:L/A:N)
Published: 2026-04-09
Source: https://osv.dev/vulnerability/JLSEC-2026-76
Type: osv

## Affected
- Julia: `OpenSSH_jll` — affected >=0 <10.3.1+0

## Details
OpenSSH before 10.3 can use unintended ECDSA algorithms. Listing of any ECDSA algorithm in PubkeyAcceptedAlgorithms or HostbasedAcceptedAlgorithms is misinterpreted to mean all ECDSA algorithms.

## References
- https://marc.info/?l=openssh-unix-dev&m=177513443901484&w=2
- https://nvd.nist.gov/vuln/detail/CVE-2026-35387
- https://www.openssh.org/releasenotes.html#10.3p1
- https://www.openwall.com/lists/oss-security/2026/04/02/3
