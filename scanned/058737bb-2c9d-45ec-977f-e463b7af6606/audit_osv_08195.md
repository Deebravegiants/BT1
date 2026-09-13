# [C] CVE-2016-15013

## Summary
Severity: Critical
Advisory: CVE-2016-15013
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-01-07
Source: https://osv.dev/vulnerability/CVE-2016-15013
Type: osv

## Details
A vulnerability was found in ForumHulp searchresults. It has been rated as critical. Affected by this issue is the function list_keywords of the file event/listener.php. The manipulation of the argument word leads to sql injection. The name of the patch is dd8a312bb285ad9735a8e1da58e9e955837b7322. It is recommended to apply a patch to fix this issue. The identifier of this vulnerability is VDB-217628.

## References
- https://vuldb.com/?ctiid.217628
- https://vuldb.com/?id.217628
- https://github.com/ForumHulp/searchresults/commit/dd8a312bb285ad9735a8e1da58e9e955837b7322
- https://github.com/ForumHulp/searchresults/pull/2
