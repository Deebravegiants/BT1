# [H] github.com/containers/image allows unexpected authenticated registry accesses

## Summary
Severity: High
Advisory: GHSA-6wvf-f2vw-3425
CVE: CVE-2024-3727
CWE: CWE-354
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2024-05-14
Source: https://github.com/advisories/GHSA-6wvf-f2vw-3425
Type: github-advisory

## Affected
- Go: `github.com/containers/image` — affected >=0 <5.30.1
- Go: `github.com/containers/image/v5` — affected >=5.30.0 <5.30.1
- Go: `github.com/containers/image/v5` — affected >=0 <5.29.3

## Details
A flaw was found in the github.com/containers/image library. This flaw allows attackers to trigger unexpected authenticated registry accesses on behalf of a victim user, causing resource exhaustion, local path traversal, and other attacks.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-3727
- https://github.com/containers/image/commit/132678b47bae29c710589012668cb85859d88385
- https://github.com/containers/image/commit/e8948046055060605bd68289d406ce149590c33a
- https://access.redhat.com/errata/RHSA-2024:0045
- https://access.redhat.com/errata/RHSA-2024:9098
- https://access.redhat.com/errata/RHSA-2024:9102
- https://access.redhat.com/errata/RHSA-2024:9960
- https://access.redhat.com/security/cve/CVE-2024-3727
- https://bugzilla.redhat.com/show_bug.cgi?id=2274767
- https://github.com/advisories/GHSA-6wvf-f2vw-3425
- https://github.com/containers/image
- https://github.com/containers/image/releases/tag/v5.29.3
- https://github.com/containers/image/releases/tag/v5.30.1
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/4HEYS34N55G7NOQZKNEXZKQVNDGEICCD
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/6B37TXOKTKDBE2V26X2NSP7JKNMZOFVP
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/CYT3D2P3OJKISNFKOOHGY6HCUCQZYAVR
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/DLND3YDQQRWVRIUPL2G5UKXP5L3VSBBT
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/DTOMYERG5ND4QFDHC4ZSGCED3T3ESRSC
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/FBZQ2ZRMFEUQ35235B2HWPSXGDCBZHFV
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/GD2GSBQTBLYADASUBHHZV2CZPTSLIPQJ
