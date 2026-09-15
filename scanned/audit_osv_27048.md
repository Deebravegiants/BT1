# [M] Coreutils: heap overflow in split --line-bytes with very long lines

## Summary
Severity: Medium
Advisory: CVE-2024-0684
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-02-06
Source: https://osv.dev/vulnerability/CVE-2024-0684
Type: osv

## Details
A flaw was found in the GNU coreutils "split" program. A heap overflow with user-controlled data of multiple hundred bytes in length could occur in the line_bytes_split() function, potentially leading to an application crash and denial of service.

## References
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/2KAURFJIEYY2BWCPN4AZDYCVMFD5J4GB/
- https://www.openwall.com/lists/oss-security/2024/01/18/2
- https://access.redhat.com/security/cve/CVE-2024-0684
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/0xxx/CVE-2024-0684.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-0684
- https://security.netapp.com/advisory/ntap-20240808-0001/
- https://bugzilla.redhat.com/show_bug.cgi?id=2258948
- https://git.savannah.gnu.org/gitweb/?p=coreutils.git
