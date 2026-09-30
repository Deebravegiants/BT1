# [M] Improper Locking in github.com/containers/storage

## Summary
Severity: Medium
Advisory: GHSA-7qw8-847f-pggm
CVE: CVE-2021-20291
CWE: CWE-400, CWE-667
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-05-10
Source: https://github.com/advisories/GHSA-7qw8-847f-pggm
Type: github-advisory

## Affected
- Go: `github.com/containers/storage` — affected >=0 <1.28.1

## Details
A deadlock vulnerability was found in `github.com/containers/storage` in versions before 1.28.1. When a container image is processed, each layer is unpacked using `tar`. If one of those layers is not a valid `tar` archive this causes an error leading to an unexpected situation where the code indefinitely waits for the tar unpacked stream, which never finishes. An attacker could use this vulnerability to craft a malicious image, which when downloaded and stored by an application using containers/storage, would then cause a deadlock leading to a Denial of Service (DoS).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-20291
- https://github.com/containers/storage/pull/860
- https://github.com/containers/storage/commit/306fcabc964470e4b3b87a43a8f6b7d698209ee1
- https://bugzilla.redhat.com/show_bug.cgi?id=1939485
- https://github.com/containers/storage
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/R5D7XL7FL24TWFMGQ3K2S72EOUSLZMKL
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/SPYOHNG2Q7DCAQZMGYLMENLKALGDLG3X
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/WX24EITRXVHDM5M223BVTJA2ODF2FSHI
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/ZNMB7O2UIXE34PGSCSOULGHPX5LIJBMM
- https://pkg.go.dev/vuln/GO-2021-0100
- https://unit42.paloaltonetworks.com/cve-2021-20291
