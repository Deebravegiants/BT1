# [C] Roo Code is vulnerable to command injection via GitHub actions workflow

## Summary
Severity: Critical
Advisory: CVE-2025-58371
Aliases: GHSA-xr6r-vj48-29f6
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:N)
Published: 2025-09-05
Source: https://osv.dev/vulnerability/CVE-2025-58371
Type: osv

## Details
Roo Code is an AI-powered autonomous coding agent that lives in users' editors. In versions 3.26.6 and below, a Github workflow used unsanitized pull request metadata in a privileged context, allowing an attacker to craft malicious input and achieve Remote Code Execution (RCE) on the Actions runner. The workflow runs with broad permissions and access to repository secrets. It is possible for an attacker to execute arbitrary commands on the runner, push or modify code in the repository, access secrets, and create malicious releases or packages, resulting in a complete compromise of the repository and its associated services. This is fixed in version 3.26.7.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/58xxx/CVE-2025-58371.json
- https://github.com/RooCodeInc/Roo-Code/security/advisories/GHSA-xr6r-vj48-29f6
- https://nvd.nist.gov/vuln/detail/CVE-2025-58371
- https://github.com/RooCodeInc/Roo-Code/commit/a0384f35d5ae3b7f66506cc62dda25d9bb673f49
