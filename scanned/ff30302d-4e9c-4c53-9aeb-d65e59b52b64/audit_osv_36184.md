# [C] ClipBucket v5 Vulnerable to Blind SQL Injection through Channel Comments

## Summary
Severity: Critical
Advisory: CVE-2026-21875
Aliases: GHSA-crpv-fmc4-j392
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-01-07
Source: https://osv.dev/vulnerability/CVE-2026-21875
Type: osv

## Details
ClipBucket v5 is an open source video sharing platform. Versions 5.5.2-#187 and below allow an attacker to perform Blind SQL Injection through the add comment section within a channel. When adding a comment within a channel, there is a POST request to the /actions/ajax.php endpoint. The obj_id parameter within the POST request to /actions/ajax.php is then used within the user_exists function of the upload/includes/classes/user.class. php file as the $id parameter. It is then used within the count function of the upload/includes/classes/db.class. php file. The $id parameter is concatenated into the query without validation or sanitization, and a user-supplied input like 1' or 1=1-- - can be used to trigger the injection. This issue does not have a fix at the time of publication.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/21xxx/CVE-2026-21875.json
- https://github.com/MacWarrior/clipbucket-v5/security/advisories/GHSA-crpv-fmc4-j392
- https://nvd.nist.gov/vuln/detail/CVE-2026-21875
