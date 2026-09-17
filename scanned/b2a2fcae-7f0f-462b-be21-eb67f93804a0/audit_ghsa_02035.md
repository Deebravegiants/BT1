# [C] Improper Authenication in Pion DTLS

## Summary
Severity: Critical
Advisory: GHSA-7gfg-6934-mqq2
CVE: CVE-2019-20786
CWE: CWE-287
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-06-29
Source: https://github.com/advisories/GHSA-7gfg-6934-mqq2
Type: github-advisory

## Affected
- Go: `github.com/pion/dtls` — affected >=0 <1.5.2

## Details
handleIncomingPacket in conn.go in Pion DTLS before 1.5.2 lacks a check for application data with epoch 0, which allows remote attackers to inject arbitrary unencrypted data after handshake completion.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-20786
- https://github.com/pion/dtls/pull/128
- https://github.com/pion/dtls/commit/fd73a5df2ff0e1fb6ae6a51e2777d7a16cc4f4e0
- https://github.com/pion/dtls
- https://github.com/pion/dtls/compare/v1.5.1...v1.5.2
- https://pkg.go.dev/vuln/GO-2020-0038
- https://www.usenix.org/conference/usenixsecurity20/presentation/fiterau-brostean
- https://www.usenix.org/system/files/sec20fall_fiterau-brostean_prepub.pdf
