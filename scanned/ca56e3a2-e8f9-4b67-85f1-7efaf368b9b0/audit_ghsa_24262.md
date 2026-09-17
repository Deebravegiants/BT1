# [H] Docker Notary Signature Algorithm Not Matched to Key vulnerability

## Summary
Severity: High
Advisory: GHSA-785h-hrf7-gqxc
CVE: CVE-2015-9258
CWE: CWE-347
Ecosystem: Go
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-785h-hrf7-gqxc
Type: github-advisory

## Affected
- Go: `github.com/docker/notary` — affected >=0 <0.1.0

## Details
In Docker Notary before 0.1, gotuf/signed/verify.go has a Signature Algorithm Not Matched to Key vulnerability. Because an attacker controls the field specifying the signature algorithm, they might (for example) be able to forge a signature by forcing a misinterpretation of an RSA-PSS key as Ed25519 elliptic-curve data.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-9258
- https://github.com/theupdateframework/notary/blob/master/docs/resources/ncc_docker_notary_audit_2015_07_31.pdf
- https://web.archive.org/web/20160305015752/https://docs.docker.com/notary/changelog
