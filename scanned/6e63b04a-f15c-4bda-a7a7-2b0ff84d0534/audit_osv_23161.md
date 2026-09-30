# [M] TicklishHoneyBee nodau db.c sql injection

## Summary
Severity: Medium
Advisory: CVE-2022-4399
CVSS: 5.5 (CVSS:3.1/AV:A/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L)
Published: 2022-12-10
Source: https://osv.dev/vulnerability/CVE-2022-4399
Type: osv

## Details
A vulnerability was found in TicklishHoneyBee nodau. It has been rated as critical. Affected by this issue is some unknown functionality of the file src/db.c. The manipulation of the argument value/name leads to sql injection. The name of the patch is 7a7d737a3929f335b9717ddbd31db91151b69ad2. It is recommended to apply a patch to fix this issue. The identifier of this vulnerability is VDB-215252.

## References
- https://vuldb.com/?id.215252
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/4xxx/CVE-2022-4399.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-4399
- https://github.com/TicklishHoneyBee/nodau/commit/7a7d737a3929f335b9717ddbd31db91151b69ad2
- https://github.com/TicklishHoneyBee/nodau/pull/26
