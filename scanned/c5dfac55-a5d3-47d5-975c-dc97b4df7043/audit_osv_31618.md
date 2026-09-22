# [H] MongoDB Shell may be susceptible to Control Character Injection via autocomplete

## Summary
Severity: High
Advisory: CVE-2025-1691
Aliases: GHSA-43g5-2wr2-q7vj
CVSS: 7.6 (CVSS:3.1/AV:N/AC:H/PR:H/UI:R/S:C/C:H/I:H/A:H)
Published: 2025-02-27
Source: https://osv.dev/vulnerability/CVE-2025-1691
Type: osv

## Details
The MongoDB Shell may be susceptible to control character injection where an attacker with control of the mongosh autocomplete feature, can use the autocompletion feature to input and run obfuscated malicious text. This requires user interaction in the form of the user using ‘tab’ to autocomplete text that is a prefix of the attacker’s prepared autocompletion. This issue affects mongosh versions prior to 2.3.9. 


The vulnerability is exploitable only when mongosh is connected to a cluster that is partially or fully controlled by an attacker.

## References
- https://jira.mongodb.org/browse/MONGOSH-2024
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/1xxx/CVE-2025-1691.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-1691
