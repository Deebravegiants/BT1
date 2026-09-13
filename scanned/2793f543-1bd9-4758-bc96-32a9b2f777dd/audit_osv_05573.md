# [H] BIT-golang-2021-29923

## Summary
Severity: High
Advisory: BIT-golang-2021-29923
Aliases: CVE-2021-29923
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-golang-2021-29923
Type: osv

## Affected
- Bitnami: `golang` — affected >=0 <1.17.0

## Details
Go before 1.17 does not properly consider extraneous zero characters at the beginning of an IP address octet, which (in some situations) allows attackers to bypass access control that is based on IP addresses, because of unexpected octal interpretation. This affects net.ParseIP and net.ParseCIDR.

## References
- https://defcon.org/html/defcon-29/dc-29-speakers.html#kaoudis
- https://github.com/golang/go/issues/30999
- https://github.com/golang/go/issues/43389
- https://github.com/sickcodes/security/blob/master/advisories/SICK-2021-016.md
- https://go-review.googlesource.com/c/go/+/325829/
- https://golang.org/pkg/net/#ParseCIDR
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/4CHKSFMHZVOBCZSSVRE3UEYNKARTBMTM/
- https://security.gentoo.org/glsa/202208-02
- https://www.oracle.com/security-alerts/cpujan2022.html
- https://nvd.nist.gov/vuln/detail/CVE-2021-29923
