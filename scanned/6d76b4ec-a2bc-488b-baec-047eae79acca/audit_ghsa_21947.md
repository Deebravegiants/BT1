# [M] Improper Privilege Management and Execution with Unnecessary Privileges in Kata Containers

## Summary
Severity: Medium
Advisory: GHSA-6978-vg2j-cc9q
CVE: CVE-2020-2023
CWE: CWE-250, CWE-269
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-02-15
Source: https://github.com/advisories/GHSA-6978-vg2j-cc9q
Type: github-advisory

## Affected
- Go: `github.com/kata-containers/agent` — affected >=0 <1.9.1
- Go: `github.com/kata-containers/agent` — affected >=1.10.0 <1.10.5
- Go: `github.com/kata-containers/agent` — affected >=1.11.0 <1.11.1
- Go: `github.com/kata-containers/runtime` — affected >=0 <1.9.1
- Go: `github.com/kata-containers/runtime` — affected >=1.10.0 <1.10.5
- Go: `github.com/kata-containers/runtime` — affected >=1.11.0 <1.11.1

## Details
Kata Containers doesn't restrict containers from accessing the guest's root filesystem device. Malicious containers can exploit this to gain code execution on the guest and masquerade as the kata-agent. This issue affects Kata Containers 1.11 versions earlier than 1.11.1; Kata Containers 1.10 versions earlier than 1.10.5; and Kata Containers 1.9 and earlier versions.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-2023
- https://github.com/kata-containers/agent/issues/791
- https://github.com/kata-containers/runtime/issues/2488
- https://github.com/kata-containers/agent/pull/792
- https://github.com/kata-containers/runtime/pull/2477
- https://github.com/kata-containers/runtime/pull/2487
- https://github.com/kata-containers
- https://github.com/kata-containers/runtime/releases/tag/1.10.5
- https://github.com/kata-containers/runtime/releases/tag/1.11.1
