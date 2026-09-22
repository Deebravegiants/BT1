# [H] CVE-2024-55555

## Summary
Severity: High
Advisory: CVE-2024-55555
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-01-07
Source: https://osv.dev/vulnerability/CVE-2024-55555
Type: osv

## Details
Invoice Ninja before 5.10.43 allows remote code execution from a pre-authenticated route when an attacker knows the APP_KEY. This is exacerbated by .env files, available from the product's repository, that have default APP_KEY values. The route/{hash} route defined in the invoiceninja/routes/client.php file can be accessed without authentication. The parameter {hash} is passed to the function decrypt that expects a Laravel ciphered value containing a serialized object. (Furthermore, Laravel contains several gadget chains usable to trigger remote command execution from arbitrary deserialization.) Therefore, an attacker in possession of the APP_KEY is able to fully control a string passed to an unserialize function.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/55xxx/CVE-2024-55555.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-55555
- https://www.synacktiv.com/advisories/invoiceninja-unauthenticated-remote-command-execution-when-appkey-known
- https://github.com/invoiceninja/invoiceninja/commit/d9302021472c3e7e23bac8c3d5fbec57a5f38f0c
