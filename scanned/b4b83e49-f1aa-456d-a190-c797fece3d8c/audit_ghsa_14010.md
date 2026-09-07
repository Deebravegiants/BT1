# [H] Moodle SQL Injection vulnerability

## Summary
Severity: High
Advisory: GHSA-7mmc-22g7-3xq2
CVE: CVE-2023-30944
CWE: CWE-89
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2023-05-02
Source: https://github.com/advisories/GHSA-7mmc-22g7-3xq2
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=0 <4.2.0-rc2

## Details
The vulnerability was found Moodle which exists due to insufficient sanitization of user-supplied data in external Wiki method for listing pages. A remote attacker can send a specially crafted request to the affected application and execute limited SQL commands within the application database.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-30944
- https://github.com/moodle/moodle/commit/5521d1d6e8bb8bebb76ad8154095f6b18ea26e7f
- https://bugzilla.redhat.com/show_bug.cgi?id=2188606
- https://github.com/moodle/moodle
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/54TM5H5PDUDYXOQ7X7PPYWP4AJDAE73I
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/MZBWRVUJF7HI53XCJPJ3YJZPOV5HBRUY
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/PBFSXRYLT4ICKJVQSRBAOUDMDRVSVBLS
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/54TM5H5PDUDYXOQ7X7PPYWP4AJDAE73I
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/MZBWRVUJF7HI53XCJPJ3YJZPOV5HBRUY
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/PBFSXRYLT4ICKJVQSRBAOUDMDRVSVBLS
- https://moodle.org/mod/forum/discuss.php?d=446286
- http://git.moodle.org/gw?p=moodle.git&a=search&h=HEAD&st=commit&s=MDL-77187
