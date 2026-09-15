# [M] CVE-2017-17824

## Summary
Severity: Medium
Advisory: CVE-2017-17824
CVSS: 4.9 (CVSS:3.0/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:N/A:N)
Published: 2017-12-21
Source: https://osv.dev/vulnerability/CVE-2017-17824
Type: osv

## Details
The Batch Manager component of Piwigo 2.9.2 is vulnerable to SQL Injection via the admin/batch_manager_unit.php element_ids parameter in unit mode. An attacker can exploit this to gain access to the data in a connected MySQL database.

## References
- https://github.com/Piwigo/Piwigo/issues/825
- https://github.com/Piwigo/Piwigo/commit/f7c8e0a947a857ff5d31dafd03842df41959b84c
- https://github.com/sahildhar/sahildhar.github.io/blob/master/research/reports/Piwigo_2.9.2/Multiple%20SQL%20Injection%20Vulnerabilities%20in%20Piwigo%202.9.2.md
