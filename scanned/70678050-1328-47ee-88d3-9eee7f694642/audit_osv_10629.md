# [M] CVE-2017-17822

## Summary
Severity: Medium
Advisory: CVE-2017-17822
CVSS: 4.9 (CVSS:3.0/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:N/A:N)
Published: 2017-12-21
Source: https://osv.dev/vulnerability/CVE-2017-17822
Type: osv

## Details
The List Users API of Piwigo 2.9.2 is vulnerable to SQL Injection via the /admin/user_list_backend.php sSortDir_0 parameter. An attacker can exploit this to gain access to the data in a connected MySQL database.

## References
- https://github.com/Piwigo/Piwigo/commit/33a03e9afb8fb00c9d8f480424d549311fe03d40
- https://github.com/Piwigo/Piwigo/issues/823
- https://github.com/sahildhar/sahildhar.github.io/blob/master/research/reports/Piwigo_2.9.2/Multiple%20SQL%20Injection%20Vulnerabilities%20in%20Piwigo%202.9.2.md
