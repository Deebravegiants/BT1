# [M] ummmmm nflpick-em.com LoadUsers.php _Load_Users sql injection

## Summary
Severity: Medium
Advisory: CVE-2022-4871
CVSS: 4.7 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:L/I:L/A:L)
Published: 2023-01-03
Source: https://osv.dev/vulnerability/CVE-2022-4871
Type: osv

## Details
A vulnerability classified as problematic was found in ummmmm nflpick-em.com up to 2.2.x. This vulnerability affects the function _Load_Users of the file html/includes/runtime/admin/JSON/LoadUsers.php. The manipulation of the argument sort leads to sql injection. The attack can be initiated remotely. The patch is identified as dd77a35942f527ea0beef5e0ec62b92e8b93211e. It is recommended to apply a patch to fix this issue. VDB-217270 is the identifier assigned to this vulnerability. NOTE: JSON entrypoint is only accessible via an admin account

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/4xxx/CVE-2022-4871.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-4871
- https://vuldb.com/?id.217270
- https://vuldb.com/?ctiid.217270
- https://github.com/ummmmm/nflpick-em.com/commit/dd77a35942f527ea0beef5e0ec62b92e8b93211e
