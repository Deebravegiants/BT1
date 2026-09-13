# [H] CVE-2021-33898

## Summary
Severity: High
Advisory: CVE-2021-33898
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-06-06
Source: https://osv.dev/vulnerability/CVE-2021-33898
Type: osv

## Details
In Invoice Ninja before 4.4.0, there is an unsafe call to unserialize() in app/Ninja/Repositories/AccountRepository.php that may allow an attacker to deserialize arbitrary PHP classes. In certain contexts, this can result in remote code execution. The attacker's input must be hosted at http://www.geoplugin.net (cleartext HTTP), and thus a successful attack requires spoofing that site or obtaining control of it.

## References
- https://github.com/invoiceninja/invoiceninja/issues/5909
