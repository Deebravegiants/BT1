# [M] ActiveAdmin CSV Injection leading to sensitive information disclosure

## Summary
Severity: Medium
Advisory: GHSA-xhvv-3jww-c487
CVE: CVE-2023-51763
CWE: CWE-1236
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:L/AC:L/PR:H/UI:R/S:C/C:L/I:L/A:L (CVSS_V3)
Published: 2023-12-28
Source: https://github.com/advisories/GHSA-xhvv-3jww-c487
Type: github-advisory

## Affected
- RubyGems: `activeadmin` — affected >=0 <3.2.0

## Details
### Impact

In ActiveAdmin versions prior to 3.2.0, maliciously crafted spreadsheet formulas could be uploaded as part of admin data that, when exported to a CSV file and the imported to a spreadsheet program like libreoffice, could lead to remote code execution and private data exfiltration.

The attacker would need privileges to upload data to the same ActiveAdmin application as the victim, and would need the victim to possibly ignore security warnings from their spreadsheet program.

### Patches

Versions 3.2.0 and above fixed the problem by escaping any data starting with `=` and other characters used by spreadsheet programs.

### Workarounds

Only turn on formula evaluation in spreadsheet programs when importing CSV after explicitly reviewing the file.  

### References

https://owasp.org/www-community/attacks/CSV_Injection
https://github.com/activeadmin/activeadmin/pull/8167

## References
- https://github.com/activeadmin/activeadmin/security/advisories/GHSA-xhvv-3jww-c487
- https://nvd.nist.gov/vuln/detail/CVE-2023-51763
- https://github.com/activeadmin/activeadmin/pull/8167
- https://github.com/activeadmin/activeadmin/commit/7af735cf657c73734fca1900cd6a5adac4ee706e
- https://github.com/activeadmin/activeadmin
- https://github.com/activeadmin/activeadmin/releases/tag/v3.2.0
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/activeadmin/CVE-2023-51763.yml
