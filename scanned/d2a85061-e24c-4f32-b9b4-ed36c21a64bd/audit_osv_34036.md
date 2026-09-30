# [M] MaxKB sandbox bypass

## Summary
Severity: Medium
Advisory: CVE-2025-53927
Aliases: GHSA-5xhm-4j3v-87m4
CVSS: 4.6 (CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:U/C:L/I:L/A:L)
Published: 2025-07-17
Source: https://osv.dev/vulnerability/CVE-2025-53927
Type: osv

## Details
MaxKB is an open-source AI assistant for enterprise. Prior to version 2.0.0, the sandbox design rules can be bypassed because MaxKB only restricts the execution permissions of files in a specific directory. Therefore, an attacker can use the `shutil.copy2` method in Python to copy the command they want to execute to the executable directory. This bypasses directory restrictions and reverse shell. Version 2.0.0 fixes the issue.

## References
- https://github.com/1Panel-dev/MaxKB/releases/tag/v2.0.0
- https://github.com/1Panel-dev/MaxKB/security/advisories/GHSA-5xhm-4j3v-87m4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/53xxx/CVE-2025-53927.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-53927
