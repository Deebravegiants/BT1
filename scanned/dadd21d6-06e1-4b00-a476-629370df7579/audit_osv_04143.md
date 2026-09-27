# [H] Apache APISIX Java Plugin Runner: Local listening file permissions in APISIX plugin runner allow a local attacker to elevate privileges

## Summary
Severity: High
Advisory: BIT-apisix-2025-27446
Aliases: CVE-2025-27446
Ecosystem: Bitnami
Published: 2025-07-16
Source: https://osv.dev/vulnerability/BIT-apisix-2025-27446
Type: osv

## Affected
- Bitnami: `apisix` — affected >=0.2.0 <3.9.0

## Details
Incorrect Permission Assignment for Critical Resource vulnerability in Apache APISIX(java-plugin-runner).

Local listening file permissions in APISIX plugin runner allow a local attacker to elevate privileges.
This issue affects Apache APISIX(java-plugin-runner): from 0.2.0 through 0.5.0.

Users are recommended to upgrade to version 0.6.0 or higher, which fixes the issue.

## References
- https://lists.apache.org/thread/qwxnxolt0j5nvjfpr0mlz6h7nrtvyzng
- https://nvd.nist.gov/vuln/detail/CVE-2025-27446
- http://www.openwall.com/lists/oss-security/2025/07/06/1
- http://www.openwall.com/lists/oss-security/2025/07/07/1
