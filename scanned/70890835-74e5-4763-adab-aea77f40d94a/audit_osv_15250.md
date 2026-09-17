# [H] CVE-2019-14823

## Summary
Severity: High
Advisory: CVE-2019-14823
CVSS: 7.4 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2019-10-14
Source: https://osv.dev/vulnerability/CVE-2019-14823
Type: osv

## Details
A flaw was found in the "Leaf and Chain" OCSP policy implementation in JSS' CryptoManager versions after 4.4.6, 4.5.3, 4.6.0, where it implicitly trusted the root certificate of a certificate chain. Applications using this policy may not properly verify the chain and could be vulnerable to attacks such as Man in the Middle.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/ENEN4DQBE6WOGEP5BQ5X62WZM7ZQEEBG/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/O53NXVKMF7PJCPMCJQHLMSYCUGDHGBVE/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/UZZWZLNALV6AOIBIHB3ZMNA5AGZMZAIY/
- https://access.redhat.com/errata/RHSA-2019:3225
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2019-14823
- https://access.redhat.com/errata/RHSA-2019:3067
