# [M] ReactPHP's HTTP server parses encoded cookie names so malicious `__Host-` and `__Secure-` cookies can be sent

## Summary
Severity: Medium
Advisory: GHSA-w3w9-vrf5-8mx8
CVE: CVE-2022-36032
CWE: CWE-20, CWE-565
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2022-09-16
Source: https://github.com/advisories/GHSA-w3w9-vrf5-8mx8
Type: github-advisory

## Affected
- Packagist: `react/http` — affected >=0.7.0 <1.7.0

## Details
### Impact

In ReactPHP's HTTP server component versions below v1.7.0, when ReactPHP is processing incoming HTTP cookie values, the cookie names are url-decoded. This may lead to cookies with prefixes like `__Host-` and `__Secure-` confused with cookies that decode to such prefix, thus leading to an attacker being able to forge cookie which is supposed to be secure. See also CVE-2020-7070 and CVE-2020-8184 for more information. 

### Patches

* https://github.com/reactphp/http/commit/663c9a3b77b71463fa7fcb76a6676ffd16979dd6 - Fixed in [reactphp/http `v1.7.0`](https://github.com/reactphp/http/releases/tag/v1.7.0)

### Workarounds

Infrastructure or DevOps can place a reverse proxy in front of the ReactPHP HTTP server to filter out any unexpected `Cookie` request headers.

### References

* CVE-2020-7070, https://bugs.php.net/bug.php?id=79699 and https://github.com/php/php-src/commit/6559fe912661ca5ce5f0eeeb591d928451428ed0
* CVE-2020-8184, https://hackerone.com/reports/895727 and https://github.com/rack/rack/commit/1f5763de6a9fe515ff84992b343d63c88104654c
* Originally introduced via https://github.com/reactphp/http/pull/175

### Credits

* Thanks to Marco Squarcina (TU Wien) for reporting this and working with us to coordinate this security advisory

### For more information

If you have any questions or comments about this advisory:

* [Join the discussion](https://github.com/orgs/reactphp/discussions/465)
* Email us at support@reactphp.org

## References
- https://github.com/reactphp/http/security/advisories/GHSA-w3w9-vrf5-8mx8
- https://nvd.nist.gov/vuln/detail/CVE-2022-36032
- https://github.com/reactphp/http/pull/175
- https://github.com/reactphp/http/commit/663c9a3b77b71463fa7fcb76a6676ffd16979dd6
- https://github.com/FriendsOfPHP/security-advisories/blob/master/react/http/CVE-2022-36032.yaml
- https://github.com/reactphp/http
- https://github.com/reactphp/http/releases/tag/v1.7.0
