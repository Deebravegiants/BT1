# [H] CVE-2019-20452

## Summary
Severity: High
Advisory: CVE-2019-20452
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-03-17
Source: https://osv.dev/vulnerability/CVE-2019-20452
Type: osv

## Details
A problem was found in Pydio Core before 8.2.4 and Pydio Enterprise before 8.2.4. A PHP object injection is present in the page plugins/core.access/src/RecycleBinManager.php. An authenticated user with basic privileges can inject objects and achieve remote code execution.

## References
- https://pydio.com/en/community/releases/pydio-core/pydio-core-pydio-enterprise-824-security-release
- https://www.certilience.fr/2020/03/cve-2019-20452-vulnerabilite-php-object-injection-pydio-core/
