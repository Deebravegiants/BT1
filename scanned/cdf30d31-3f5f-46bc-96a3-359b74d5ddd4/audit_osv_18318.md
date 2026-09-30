# [H] CVE-2020-26124

## Summary
Severity: High
Advisory: CVE-2020-26124
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-10-02
Source: https://osv.dev/vulnerability/CVE-2020-26124
Type: osv

## Details
openmediavault before 4.1.36 and 5.x before 5.5.12 allows authenticated PHP code injection attacks, via the sortfield POST parameter of rpc.php, because json_encode_safe is not used in config/databasebackend.inc. Successful exploitation allows arbitrary command execution on the underlying operating system as root.

## References
- https://www.openmediavault.org/?p=2797
- https://github.com/openmediavault/openmediavault/commit/ebb51bbf5a39f4955eab0073bf87f2a31926d85d
- http://packetstormsecurity.com/files/160223/OpenMediaVault-rpc.php-Authenticated-PHP-Code-Injection.html
