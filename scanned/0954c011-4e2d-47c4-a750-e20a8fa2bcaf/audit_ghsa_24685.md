# [C] OpenStack Swauth object/proxy server writing Auth Token to log file

## Summary
Severity: Critical
Advisory: GHSA-qhq8-xwqv-pvv9
CVE: CVE-2017-16613
CWE: CWE-287
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-qhq8-xwqv-pvv9
Type: github-advisory

## Affected
- PyPI: `swauth` — affected >=0 <1.3.0

## Details
An issue was discovered in middleware.py in OpenStack Swauth through 1.2.0 when used with OpenStack Swift through 2.15.1. The Swift object store and proxy server are saving (unhashed) tokens retrieved from the Swauth middleware authentication mechanism to a log file as part of a GET URI. This allows attackers to bypass authentication by inserting a token into an X-Auth-Token header of a new request. NOTE: github.com/openstack/swauth URLs do not mean that Swauth is maintained by an official OpenStack project team.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-16613
- https://github.com/openstack/swauth/commit/70af7986265a3defea054c46efc82d0698917298
- https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=882314
- https://bugs.launchpad.net/swift/+bug/1655781
- https://github.com/openstack/swauth
- https://github.com/pypa/advisory-database/tree/main/vulns/swauth/PYSEC-2017-84.yaml
- https://web.archive.org/web/20200227140059/http://www.securityfocus.com/bid/101926
- https://www.debian.org/security/2017/dsa-4044
