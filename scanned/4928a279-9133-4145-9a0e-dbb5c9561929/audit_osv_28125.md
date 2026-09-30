# [M] CSV Injection in exported history CSV files

## Summary
Severity: Medium
Advisory: CVE-2024-28111
Aliases: GHSA-fqh6-v4qp-65fv
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N)
Published: 2024-03-06
Source: https://osv.dev/vulnerability/CVE-2024-28111
Type: osv

## Details
Canarytokens helps track activity and actions on a network. Canarytokens.org supports exporting the history of a Canarytoken's incidents in CSV format. The generation of these CSV files is vulnerable to a CSV Injection vulnerability. This flaw can be used by an attacker who discovers an HTTP-based Canarytoken to target the Canarytoken's owner, if the owner exports the incident history to CSV and opens in a reader application such as Microsoft Excel. The impact is that this issue could lead to code execution on the machine on which the CSV file is opened. Version sha-c595a1f8 contains a fix for this issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/28xxx/CVE-2024-28111.json
- https://github.com/thinkst/canarytokens/security/advisories/GHSA-fqh6-v4qp-65fv
- https://nvd.nist.gov/vuln/detail/CVE-2024-28111
- https://github.com/thinkst/canarytokens/commit/c595a1f884b986da2ca05aa5bff9ae5f93c6a4aa
