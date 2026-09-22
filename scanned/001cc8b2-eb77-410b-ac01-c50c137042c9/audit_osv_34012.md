# [M] Meshtastic allows Command Injection in GitHub Action

## Summary
Severity: Medium
Advisory: CVE-2025-53637
Aliases: GHSA-6mwm-v2vv-pp96
CVSS: 4.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:N/A:N)
Published: 2025-07-10
Source: https://osv.dev/vulnerability/CVE-2025-53637
Type: osv

## Details
Meshtastic is an open source mesh networking solution. The main_matrix.yml GitHub Action is triggered by the pull_request_target event, which has extensive permissions, and can be initiated by an attacker who forked the repository and created a pull request. In the shell code execution part, user-controlled input is interpolated unsafely into the code. If this were to be exploited, attackers could inject unauthorized code into the repository. This vulnerability is fixed in 2.6.6.

## References
- https://github.com/meshtastic/firmware/blob/3fd47d9713e7d1b6866c48cf218e2435741651a2/.github/workflows/main_matrix.yml#L34-L41
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/53xxx/CVE-2025-53637.json
- https://github.com/meshtastic/firmware/security/advisories/GHSA-6mwm-v2vv-pp96
- https://nvd.nist.gov/vuln/detail/CVE-2025-53637
