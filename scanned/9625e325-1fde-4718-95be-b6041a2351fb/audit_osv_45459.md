# [M] Applications that use Wget to access a remote resource using shorthand URLs and pass arbitrary user...

## Summary
Severity: Medium
Advisory: JLSEC-2026-119
Ecosystem: Julia
CVSS: 6.5 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:L/I:L/A:L)
Published: 2026-04-15
Source: https://osv.dev/vulnerability/JLSEC-2026-119
Type: osv

## Affected
- Julia: `wget_jll` — affected >=0 <1.25.0+0

## Details
Applications that use Wget to access a remote resource using shorthand URLs and pass arbitrary user credentials in the URL are vulnerable. In these cases attackers can enter crafted credentials which will cause Wget to access an arbitrary host.

## References
- http://www.openwall.com/lists/oss-security/2024/11/18/6
- https://git.savannah.gnu.org/cgit/wget.git/commit/?id=c419542d956a2607bbce5df64b9d378a8588d778
- https://github.com/advisories/GHSA-mqrm-h2pw-9j9r
- https://jfrog.com/blog/cve-2024-10524-wget-zero-day-vulnerability
- https://jfrog.com/blog/cve-2024-10524-wget-zero-day-vulnerability/
- https://nvd.nist.gov/vuln/detail/CVE-2024-10524
- https://seclists.org/oss-sec/2024/q4/107
- https://security.netapp.com/advisory/ntap-20250321-0007
- https://security.netapp.com/advisory/ntap-20250321-0007/
