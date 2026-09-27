# [M] CVE-2020-5225

## Summary
Severity: Medium
Advisory: CVE-2020-5225
Aliases: GHSA-6gc6-m364-85ww
CVSS: 5.4 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N)
Published: 2020-01-24
Source: https://osv.dev/vulnerability/CVE-2020-5225
Type: osv

## Details
Log injection in SimpleSAMLphp before version 1.18.4. The www/erroreport.php script, which receives error reports and sends them via email to the system administrator, did not properly sanitize the report identifier obtained from the request. This allows an attacker, under specific circumstances, to inject new log lines by manually crafting this report ID. When configured to use the file logging handler, SimpleSAMLphp will output all its logs by appending each log line to a given file. Since the reportID parameter received in a request sent to www/errorreport.php was not properly sanitized, it was possible to inject newline characters into it, effectively allowing a malicious user to inject new log lines with arbitrary content.

## References
- https://github.com/simplesamlphp/simplesamlphp/security/advisories/GHSA-6gc6-m364-85ww
- https://simplesamlphp.org/security/202001-02
