# [C] Inadequate validation of retrieved subdomains may lead to a Remote Code Execution in reconFTW

## Summary
Severity: Critical
Advisory: CVE-2023-46117
Aliases: GHSA-fxwr-vr9x-wvjp
CVSS: 9.6 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:H)
Published: 2023-10-20
Source: https://osv.dev/vulnerability/CVE-2023-46117
Type: osv

## Details
reconFTW is a tool designed to perform automated recon on a target domain by running the best set of tools to perform scanning and finding out vulnerabilities. A vulnerability has been identified in reconftw where inadequate validation of retrieved subdomains may lead to a Remote Code Execution (RCE) attack. An attacker can exploit this vulnerability by crafting a malicious CSP entry on it's own domain. Successful exploitation can lead to the execution of arbitrary code within the context of the application, potentially compromising the system. This issue has been addressed in version 2.7.1.1 and all users are advised to upgrade. There are no known workarounds for this vulnerability.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/46xxx/CVE-2023-46117.json
- https://github.com/six2dez/reconftw/security/advisories/GHSA-fxwr-vr9x-wvjp
- https://nvd.nist.gov/vuln/detail/CVE-2023-46117
- https://github.com/six2dez/reconftw/commit/e639de356c0880fe5fe01a32de9d0c58afb5f086
