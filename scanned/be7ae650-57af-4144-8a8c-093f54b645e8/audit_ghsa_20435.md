# [C] Authentication Bypass in ADOdb/ADOdb

## Summary
Severity: Critical
Advisory: GHSA-65mj-7c86-79jf
CVE: CVE-2021-3850
CWE: CWE-287, CWE-305
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2022-01-27
Source: https://github.com/advisories/GHSA-65mj-7c86-79jf
Type: github-advisory

## Affected
- Packagist: `adodb/adodb-php` — affected >=0 <5.20.21
- Packagist: `adodb/adodb-php` — affected >=5.21.0 <5.21.4

## Details
### Impact

An attacker can inject values into a PostgreSQL connection string by providing a parameter surrounded by single quotes.

Depending on how the library is used in the client software, this may allow an attacker to bypass the login process, gain access to the server's IP address, etc.

### Patches

The vulnerability is fixed in ADOdb versions 5.20.21 (952de6c4273d9b1e91c2b838044f8c2111150c29) and 5.21.4 or later (b4d5ce70034c5aac3a1d51d317d93c037a0938d2).

The simplest patch is to delete line 29 in `drivers/adodb-postgres64.inc.php`:

```php
diff --git a/drivers/adodb-postgres64.inc.php b/drivers/adodb-postgres64.inc.php
index d04b7f67..729d7141 100644
--- a/drivers/adodb-postgres64.inc.php
+++ b/drivers/adodb-postgres64.inc.php
@@ -26,7 +26,6 @@ function adodb_addslashes($s)
 {
    $len = strlen($s);
    if ($len == 0) return "''";
-   if (strncmp($s,"'",1) === 0 && substr($s,$len-1) == "'") return $s; // already quoted
 
    return "'".addslashes($s)."'";
 }
```

### Workarounds

Ensure the parameters passed to *ADOConnection::connect()* or related functions (_nConnect()_, _pConnect()_) are not surrounded by single quotes.

### Credits

Thanks to **Emmet Leahy** (@meme-lord) of Sorcery Ltd for reporting this vulnerability, and to the [huntr](https://huntr.dev/) team for their support.

### References

- Original issue report https://huntr.dev/bounties/bdf5f216-4499-4225-a737-b28bc6f5801c/
- ADOdb reference issue #793 

### For more information

If you have any questions or comments about this advisory:
* Add a note in issue #793
* Contact the maintainers on [Gitter](https://gitter.im/adodb/adodb)

## References
- https://github.com/ADOdb/ADOdb/security/advisories/GHSA-65mj-7c86-79jf
- https://nvd.nist.gov/vuln/detail/CVE-2021-3850
- https://github.com/ADOdb/ADOdb/issues/793
- https://github.com/ADOdb/ADOdb/commit/952de6c4273d9b1e91c2b838044f8c2111150c29
- https://github.com/ADOdb/ADOdb/commit/b4d5ce70034c5aac3a1d51d317d93c037a0938d2
- https://github.com/ADOdb/ADOdb
- https://huntr.dev/bounties/bdf5f216-4499-4225-a737-b28bc6f5801c
- https://lists.debian.org/debian-lts-announce/2022/02/msg00006.html
- https://www.debian.org/security/2022/dsa-5101
