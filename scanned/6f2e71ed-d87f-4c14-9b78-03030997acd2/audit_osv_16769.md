# [C] CVE-2019-9642

## Summary
Severity: Critical
Advisory: CVE-2019-9642
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-06-05
Source: https://osv.dev/vulnerability/CVE-2019-9642
Type: osv

## Details
An issue was discovered in proxy.php in pydio-core in Pydio through 8.2.2. Through an unauthenticated request, it possible to evaluate malicious PHP code by placing it on the fourth line of a .php file, as demonstrated by a PoC.php created by the guest account, with execution via a proxy.php?hash=../../../../../var/lib/pydio/data/personal/guest/PoC.php request. This is related to plugins/action.share/src/Store/ShareStore.php.

## References
- https://pydio.com/en/community/releases/pydio-core/pydio-core-pydio-enterprise-823-security-release
- https://github.com/pydio/pydio-core/commits/develop/core/src/proxy.php
