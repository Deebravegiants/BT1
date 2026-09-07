# [M] Moodle External Control of File Name or Path vulnerability

## Summary
Severity: Medium
Advisory: GHSA-22gj-8qj2-fj46
CVE: CVE-2023-30943
CWE: CWE-610, CWE-73
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2023-05-02
Source: https://github.com/advisories/GHSA-22gj-8qj2-fj46
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=0 <4.2.0-rc2

## Details
The vulnerability was found Moodle which exists because the application allows a user to control path of the older to create in TinyMCE loaders. A remote user can send a specially crafted HTTP request and create arbitrary folders on the system.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-30943
- https://github.com/moodle/moodle/commit/59d42e1ed23f916dcb47d53c745bef18a116d800
- https://bugzilla.redhat.com/show_bug.cgi?id=2188605
- https://github.com/moodle/moodle
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/54TM5H5PDUDYXOQ7X7PPYWP4AJDAE73I
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/MZBWRVUJF7HI53XCJPJ3YJZPOV5HBRUY
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/PBFSXRYLT4ICKJVQSRBAOUDMDRVSVBLS
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/54TM5H5PDUDYXOQ7X7PPYWP4AJDAE73I
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/MZBWRVUJF7HI53XCJPJ3YJZPOV5HBRUY
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/PBFSXRYLT4ICKJVQSRBAOUDMDRVSVBLS
- https://moodle.org/mod/forum/discuss.php?d=446285
- http://git.moodle.org/gw?p=moodle.git&a=search&h=HEAD&st=commit&s=MDL-77718
