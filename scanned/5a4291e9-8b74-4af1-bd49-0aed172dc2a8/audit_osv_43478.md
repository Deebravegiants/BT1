# [M] Wazuh 4.0.0 < 4.14.6 Path Traversal DoS via Agent Enrollment

## Summary
Severity: Medium
Advisory: CVE-2026-74038
Aliases: GHSA-573w-mqw4-jvmr
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:A/VC:N/VI:L/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-18
Source: https://osv.dev/vulnerability/CVE-2026-74038
Type: osv

## Details
Wazuh 4.0.0 before 4.14.6 contains a path traversal vulnerability that allows unauthenticated remote attackers to cause denial of service by enrolling an agent with a dot-sequence name such as ".." through the enrollment port. Attackers exploit insufficient validation in OS_IsValidName() and unsafe path concatenation in delete_diff() to resolve the traversal to the parent queue directory, causing its subdirectories to be removed and stopping all Wazuh services requiring manual recovery.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74038.json
- https://github.com/wazuh/wazuh/security/advisories/GHSA-573w-mqw4-jvmr
- https://nvd.nist.gov/vuln/detail/CVE-2026-74038
- https://www.vulncheck.com/advisories/wazuh-path-traversal-dos-via-agent-enrollment
- https://github.com/wazuh/wazuh/pull/35833
- https://github.com/wazuh/wazuh
