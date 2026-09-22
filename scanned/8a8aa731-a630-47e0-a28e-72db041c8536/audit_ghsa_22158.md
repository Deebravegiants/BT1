# [H] Pimcore Unserialize Remote Code Execution

## Summary
Severity: High
Advisory: GHSA-7hqr-j26m-gmwp
CVE: CVE-2019-10867
CWE: CWE-502
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-7hqr-j26m-gmwp
Type: github-advisory

## Affected
- Packagist: `pimcore/pimcore` — affected >=0 <5.7.1

## Details
An issue was discovered in Pimcore before 5.7.1. An attacker with classes permission can send a POST request to `/admin/class/bulk-commit`, which will make it possible to exploit the unserialize function when passing untrusted values in the data parameter to `bundles/AdminBundle/Controller/Admin/DataObject/ClassController.php`.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10867
- https://github.com/pimcore/pimcore/commit/38a29e2f4f5f060a73974626952501cee05fda73
- https://blog.certimetergroup.com/it/articolo/security/polyglot_phar_deserialization_to_rce
- https://github.com/pimcore/pimcore
- https://snyk.io/vuln/SNYK-PHP-PIMCOREPIMCORE-173998
- https://www.exploit-db.com/exploits/46783
- http://packetstormsecurity.com/files/152667/Pimcore-Unserialize-Remote-Code-Execution.html
- http://www.rapid7.com/db/modules/exploit/multi/http/pimcore_unserialize_rce
