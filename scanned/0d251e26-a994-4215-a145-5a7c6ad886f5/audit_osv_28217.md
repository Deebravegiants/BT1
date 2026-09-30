# [C] FreeScout OS Command Injection vulnerability

## Summary
Severity: Critical
Advisory: CVE-2024-29185
Aliases: GHSA-7p9x-ch4c-vqj9
CVSS: 9.0 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:H/I:H/A:H)
Published: 2024-03-22
Source: https://osv.dev/vulnerability/CVE-2024-29185
Type: osv

## Details
FreeScout is a self-hosted help desk and shared mailbox. Versions prior to 1.8.128 are vulnerable to OS Command Injection in the /public/tools.php source file. The value of the php_path parameter is being executed as an OS command by the shell_exec function, without validating it. This allows an adversary to execute malicious OS commands on the server. A practical demonstration of the successful command injection attack extracted the /etc/passwd file of the server. This represented the complete compromise of the server hosting the FreeScout application. This attack requires an attacker to know the `App_Key` of the application. This limitation makes the Attack Complexity to be High. If an attacker gets hold of the `App_Key`, the attacker can compromise the Complete server on which the application is deployed. Version 1.8.128 contains a patch for this issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/29xxx/CVE-2024-29185.json
- https://github.com/freescout-helpdesk/freescout/security/advisories/GHSA-7p9x-ch4c-vqj9
- https://nvd.nist.gov/vuln/detail/CVE-2024-29185
