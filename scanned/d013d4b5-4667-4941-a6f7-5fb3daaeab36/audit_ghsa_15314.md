# [H] Apache DolphinScheduler: RCE by arbitrary js execution

## Summary
Severity: High
Advisory: GHSA-m9q4-p56m-mc6q
CVE: CVE-2024-29831
CWE: CWE-20
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-08-12
Source: https://github.com/advisories/GHSA-m9q4-p56m-mc6q
Type: github-advisory

## Affected
- Maven: `org.apache.dolphinscheduler:dolphinscheduler` — affected >=0 <3.2.2

## Details
Improper Input Validation vulnerability in Apache DolphinScheduler. An authenticated user can cause arbitrary, unsandboxed javascript to be executed on the server. If you are using the switch task plugin, please upgrade to version 3.2.2.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-29831
- https://github.com/apache/dolphinscheduler
- https://lists.apache.org/thread/x1ch0x5om3srtbnp7rtsvdszho3mdrq0
- http://www.openwall.com/lists/oss-security/2024/08/09/6
