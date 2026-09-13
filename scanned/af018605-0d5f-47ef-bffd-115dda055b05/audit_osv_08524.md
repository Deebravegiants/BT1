# [H] CVE-2016-4074

## Summary
Severity: High
Advisory: CVE-2016-4074
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-05-06
Source: https://osv.dev/vulnerability/CVE-2016-4074
Type: osv

## Details
The jv_dump_term function in jq 1.5 allows remote attackers to cause a denial of service (stack consumption and application crash) via a crafted JSON file. This issue has been fixed in jq 1.6_rc1-r0.

## References
- http://www.openwall.com/lists/oss-security/2016/04/24/3
- http://www.openwall.com/lists/oss-security/2016/04/24/4
- https://github.com/hashicorp/consul/issues/10263
- https://github.com/stedolan/jq/
- https://github.com/NixOS/nixpkgs/pull/18908
- https://github.com/stedolan/jq/issues/1136
