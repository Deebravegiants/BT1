# [M] OpenSIPS has vulnerability in the ds_is_in_list() function

## Summary
Severity: Medium
Advisory: CVE-2023-28099
Aliases: GHSA-pfm5-6vhv-3ff3
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-03-15
Source: https://osv.dev/vulnerability/CVE-2023-28099
Type: osv

## Details
OpenSIPS is a Session Initiation Protocol (SIP) server implementation. Prior to versions 3.1.9 and 3.2.6, if `ds_is_in_list()` is used with an invalid IP address string (`NULL` is illegal input), OpenSIPS will attempt to print a string from a random address (stack garbage), which could lead to a crash.  All users of `ds_is_in_list()` without the `$si` variable as 1st parameter could be affected by this vulnerability to a larger, lesser or no extent at all, depending if the data passed to the function is a valid IPv4 or IPv6 address string or not. Fixes will are available starting with the 3.1.9 and 3.2.6 minor releases. There are no known workarounds.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/28xxx/CVE-2023-28099.json
- https://github.com/OpenSIPS/opensips/security/advisories/GHSA-pfm5-6vhv-3ff3
- https://nvd.nist.gov/vuln/detail/CVE-2023-28099
- https://github.com/OpenSIPS/opensips/issues/2780
- https://github.com/OpenSIPS/opensips/commit/e2f13d374
