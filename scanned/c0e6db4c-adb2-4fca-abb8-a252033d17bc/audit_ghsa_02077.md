# [H] Helm uses crypto package vulnerable to panic from malformed X.509 certificate

## Summary
Severity: High
Advisory: GHSA-cjjc-xp8v-855w
CVE: CVE-2020-7919
CWE: CWE-295
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-06-23
Source: https://github.com/advisories/GHSA-cjjc-xp8v-855w
Type: github-advisory

## Affected
- Go: `github.com/helm/helm` — affected >=2.0.0 <2.16.8
- Go: `helm.sh/helm/v3` — affected >=3.0.0 <3.1.0
- Go: `golang.org/x/crypto` — affected >=0 <0.0.0-20200124225646-8b5121be2f68

## Details
The Helm core maintainers have identified a high severity security vulnerability in Go's `crypto` package affecting all versions prior to Helm 2.16.8 and Helm 3.1.0.

Thanks to @ravin9249 for identifying the vulnerability.

### Impact

Go before 1.12.16 and 1.13.x before 1.13.7 (and the `crypto/cryptobyte` package before 0.0.0-20200124225646-8b5121be2f68 for Go) allows attacks on clients resulting in a panic via a malformed X.509 certificate. This may allow a remote attacker to cause a denial of service.

### Patches

A patch to compile Helm against Go 1.14.4 has been provided for Helm 2 and is available in Helm 2.16.8. Helm 3.1.0 and newer are compiled against Go 1.13.7+.

### Workarounds

No workaround is available. Users are urged to upgrade.

### References

- https://nvd.nist.gov/vuln/detail/CVE-2020-7919
- https://github.com/helm/helm/pull/8288

### For more information

If you have any questions or comments about this advisory:

* Open an issue in [the Helm repository](https://github.com/helm/helm/issues)
* For security-specific issues, email us at <cncf-helm-security@lists.cncf.io>

## References
- https://github.com/helm/helm/security/advisories/GHSA-cjjc-xp8v-855w
- https://nvd.nist.gov/vuln/detail/CVE-2020-7919
- https://github.com/helm/helm
- https://go.dev/cl/216677
- https://go.dev/cl/216680
- https://go.dev/issue/36837
- https://go.googlesource.com/go/+/b13ce14c4a6aa59b7b041ad2b6eed2d23e15b574
- https://groups.google.com/forum/#!forum/golang-announce
- https://groups.google.com/forum/#!topic/golang-announce/-sdUB4VEQkA
- https://groups.google.com/forum/#!topic/golang-announce/Hsw4mHYc470
- https://groups.google.com/g/golang-announce/c/Hsw4mHYc470
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/S43VLYRURELDWX4D5RFOYBNFGO6CGBBC
- https://pkg.go.dev/vuln/GO-2022-0229
- https://security.netapp.com/advisory/ntap-20200327-0001
- https://www.debian.org/security/2021/dsa-4848
- https://www.oracle.com/security-alerts/cpuApr2021.html
