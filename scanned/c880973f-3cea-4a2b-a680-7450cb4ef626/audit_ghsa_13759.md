# [H] Calico Typha denial of service vulnerability

## Summary
Severity: High
Advisory: GHSA-5r5h-q934-cccp
CVE: CVE-2023-41378
CWE: CWE-400, CWE-755
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-11-06
Source: https://github.com/advisories/GHSA-5r5h-q934-cccp
Type: github-advisory

## Affected
- Go: `github.com/projectcalico/calico` — affected >=3.26.0 <3.26.3
- Go: `github.com/projectcalico/calico` — affected >=0

## Details
In certain conditions for Calico Typha (v3.26.2, v3.25.1 and below), and Calico Enterprise Typha (v3.17.1, v3.16.3, v3.15.3 and below), a client TLS handshake can block the Calico Typha server indefinitely, resulting in denial of service. The TLS Handshake() call is performed inside the main server handle for loop without any timeout allowing an unclean TLS handshake to block the main loop indefinitely while other connections will be idle waiting for that handshake to finish.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-41378
- https://github.com/projectcalico/calico/pull/7908
- https://github.com/projectcalico/calico/pull/7993
- https://github.com/projectcalico/calico/commit/2ebc1f92ecc39332cf1d55ba676d9101af24982f
- https://github.com/projectcalico/calico/commit/ad8bd001e650ec7742ac30e58247e7eef5956125
- https://github.com/projectcalico/calico
- https://www.tigera.io/security-bulletins-tta-2023-001
