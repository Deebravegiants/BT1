# [C] OrangeHRM is Vulnerable to Code Execution Through Arbitrary File Write from Sendmail Parameter Injection

## Summary
Severity: Critical
Advisory: CVE-2025-66224
Aliases: GHSA-2w7w-h5wv-xr55
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H)
Published: 2025-11-29
Source: https://osv.dev/vulnerability/CVE-2025-66224
Type: osv

## Details
OrangeHRM is a comprehensive human resource management (HRM) system. From version 5.0 to 5.7, the application contains an input-neutralization flaw in its mail configuration and delivery workflow that allows user-controlled values to flow directly into the system’s sendmail command. Because these values are not sanitized or constrained before being incorporated into the command execution path, certain sendmail behaviors can be unintentionally invoked during email processing. This makes it possible for the application to write files on the server as part of the mail-handling routine, and in deployments where those files end up in web-accessible locations, the behavior can be leveraged to achieve execution of attacker-controlled content. The issue stems entirely from constructing OS-level command strings using unsanitized input within the mail-sending logic. This issue has been patched in version 5.8.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/66xxx/CVE-2025-66224.json
- https://github.com/orangehrm/orangehrm/security/advisories/GHSA-2w7w-h5wv-xr55
- https://nvd.nist.gov/vuln/detail/CVE-2025-66224
