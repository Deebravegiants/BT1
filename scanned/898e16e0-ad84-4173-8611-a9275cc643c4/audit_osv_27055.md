# [M] Improper Restriction of Excessive Authentication Attempts in phpipam/phpipam

## Summary
Severity: Medium
Advisory: CVE-2024-0787
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2024-11-15
Source: https://osv.dev/vulnerability/CVE-2024-0787
Type: osv

## Details
phpIPAM version 1.5.1 contains a vulnerability where an attacker can bypass the IP block mechanism to brute force passwords for users by using the 'X-Forwarded-For' header. The issue lies in the 'get_user_ip()' function in 'class.Common.php' at lines 1044 and 1045, where the presence of the 'X-Forwarded-For' header is checked and used instead of 'REMOTE_ADDR'. This vulnerability allows attackers to perform brute force attacks on user accounts, including the admin account. The issue is fixed in version 1.7.0.

## References
- https://huntr.com/bounties/840cb582-1feb-43ab-9cc4-e4b5a63c5bab
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/0xxx/CVE-2024-0787.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-0787
- https://github.com/phpipam/phpipam/commit/55c2056068be9f1359e967fcff64db6b7f4d00b5
