# [C] In GnuPG before 2.5.17, a crafted CMS (S/MIME) EnvelopedData message carrying an oversized wrapped...

## Summary
Severity: Critical
Advisory: JLSEC-2026-564
Ecosystem: Julia
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-27
Source: https://osv.dev/vulnerability/JLSEC-2026-564
Type: osv

## Affected
- Julia: `GnuPG_jll` — affected >=2.5.16+0 <2.5.17+0

## Details
In GnuPG before 2.5.17, a crafted CMS (S/MIME) EnvelopedData message carrying an oversized wrapped session key can cause a stack-based buffer overflow in gpg-agent during PKDECRYPT--kem=CMS handling. This can easily be leveraged for denial of service; however, there is also memory corruption that could lead to remote code execution.

## References
- https://access.redhat.com/security/cve/CVE-2026-24881
- https://bugzilla.redhat.com/show_bug.cgi?id=2433480
- https://dev.gnupg.org/T8044
- https://github.com/advisories/GHSA-5w36-x85h-pphm
- https://nvd.nist.gov/vuln/detail/CVE-2026-24881
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-24881.json
- https://www.openwall.com/lists/oss-security/2026/01/27/8
