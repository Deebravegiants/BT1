# [H] CVE-2026-24881

## Summary
Severity: High
Advisory: CVE-2026-24881
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-01-27
Source: https://osv.dev/vulnerability/CVE-2026-24881
Type: osv

## Details
In GnuPG before 2.5.17, a crafted CMS (S/MIME) EnvelopedData message carrying an oversized wrapped session key can cause a stack-based buffer overflow in gpg-agent during PKDECRYPT--kem=CMS handling. This can easily be leveraged for denial of service; however, there is also memory corruption that could lead to remote code execution.

## References
- https://dev.gnupg.org/T8044
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-24881.json
- https://www.openwall.com/lists/oss-security/2026/01/27/8
- https://access.redhat.com/security/cve/CVE-2026-24881
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/24xxx/CVE-2026-24881.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-24881
- https://bugzilla.redhat.com/show_bug.cgi?id=2433480
