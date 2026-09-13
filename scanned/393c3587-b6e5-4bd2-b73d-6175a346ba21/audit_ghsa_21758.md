# [M] Permissive parameters and privilege escalation

## Summary
Severity: Medium
Advisory: GHSA-mrq8-53r4-3j5m
CVE: CVE-2018-20301
CWE: CWE-20
Ecosystem: Hex
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-02-10
Source: https://github.com/advisories/GHSA-mrq8-53r4-3j5m
Type: github-advisory

## Affected
- Hex: `coherence` — affected >=0 <0.5.2

## Details
An issue was discovered in Steve Pallen Coherence before 0.5.2 that is similar to a Mass Assignment vulnerability. In particular, "registration" endpoints (e.g., creating, editing, updating) allow users to update any coherence_fields data. For example, users can automatically confirm their accounts by sending the confirmed_at parameter with their registration request.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-20301
- https://github.com/smpallen99/coherence/issues/270
- https://github.com/smpallen99/coherence
