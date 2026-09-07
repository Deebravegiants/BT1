# [H] Calico privilege escalation vulnerability

## Summary
Severity: High
Advisory: GHSA-6362-gv4m-53ww
CVE: CVE-2024-33522
CWE: CWE-269
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-04-30
Source: https://github.com/advisories/GHSA-6362-gv4m-53ww
Type: github-advisory

## Affected
- Go: `github.com/projectcalico/calico` — affected >=0 <3.26.5
- Go: `github.com/projectcalico/calico` — affected >=3.27.0 <3.27.3

## Details
In vulnerable versions of Calico (v3.27.2 and below), Calico Enterprise (v3.19.0-1, v3.18.1, v3.17.3 and below), and Calico Cloud (v19.2.0 and below), an attacker who has local access to the Kubernetes node, can escalate their privileges by exploiting a vulnerability in the Calico CNI install binary. The issue arises from an incorrect SUID (Set User ID) bit configuration in the binary, combined with the ability to control the input binary, allowing an attacker to execute an arbitrary binary with elevated privileges.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-33522
- https://github.com/projectcalico/calico/issues/7981
- https://github.com/projectcalico/calico/pull/8447
- https://github.com/projectcalico/calico/pull/8517
- https://github.com/advisories/GHSA-6362-gv4m-53ww
- https://github.com/projectcalico/calico
- https://pkg.go.dev/vuln/GO-2024-2801
- https://www.tigera.io/security-bulletins-tta-2024-001
