# [C] Command Injection in mudler/localai

## Summary
Severity: Critical
Advisory: CVE-2024-5181
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-06-26
Source: https://osv.dev/vulnerability/CVE-2024-5181
Type: osv

## Details
A command injection vulnerability exists in the mudler/localai version 2.14.0. The vulnerability arises from the application's handling of the backend parameter in the configuration file, which is used in the name of the initialized process. An attacker can exploit this vulnerability by manipulating the path of the vulnerable binary file specified in the backend parameter, allowing the execution of arbitrary code on the system. This issue is due to improper neutralization of special elements used in an OS command, leading to potential full control over the affected system.

## References
- https://huntr.com/bounties/c6e3cb58-6fa4-4207-bb92-ae7644174661
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/5xxx/CVE-2024-5181.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-5181
- https://github.com/mudler/localai/commit/1a3dedece06cab1acc3332055d285ac540a47f0e
