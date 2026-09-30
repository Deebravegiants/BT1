# [C] CVE-2021-25294

## Summary
Severity: Critical
Advisory: CVE-2021-25294
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-01-18
Source: https://osv.dev/vulnerability/CVE-2021-25294
Type: osv

## Details
OpenCATS through 0.9.5-3 unsafely deserializes index.php?m=activity requests, leading to remote code execution. This occurs because lib/DataGrid.php calls unserialize for the parametersactivity:ActivityDataGrid parameter. The PHP object injection exploit chain can leverage an __destruct magic method in guzzlehttp.

## References
- https://www.opencats.org/news/
- https://github.com/snoopysecurity/snoopysecurity.github.io/blob/master/web-application-security/2021/01/16/09_opencats_php_object_injection.html
- https://snoopysecurity.github.io/web-application-security/2021/01/16/09_opencats_php_object_injection.html
