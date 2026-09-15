# [H] BIT-node-2024-27980

## Summary
Severity: High
Advisory: BIT-node-2024-27980
Aliases: BIT-node-min-2024-27980, CVE-2024-27980
Ecosystem: Bitnami
Published: 2025-01-10
Source: https://osv.dev/vulnerability/BIT-node-2024-27980
Type: osv

## Affected
- Bitnami: `node` — affected >=21.0.0 <21.7.3

## Details
Due to the improper handling of batch files in child_process.spawn / child_process.spawnSync, a malicious command line argument can inject arbitrary commands and achieve code execution even if the shell option is not enabled.

## References
- http://www.openwall.com/lists/oss-security/2024/04/10/15
- http://www.openwall.com/lists/oss-security/2024/07/11/6
- http://www.openwall.com/lists/oss-security/2024/07/19/3
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/5MZN6PFXHTCCUENAKZXTGWPKUAHI6E2W/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/JUWBYDVCUSCX7YWTBX75LADMCVYFBGKU/
- https://nvd.nist.gov/vuln/detail/CVE-2024-27980
