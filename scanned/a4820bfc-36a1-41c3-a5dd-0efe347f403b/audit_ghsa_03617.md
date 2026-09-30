# [M] Possible Information Leak / Session Hijack Vulnerability in Rack

## Summary
Severity: Medium
Advisory: GHSA-hrqr-hxpp-chr3
CVE: CVE-2019-16782
CWE: CWE-203, CWE-208
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2019-12-18
Source: https://github.com/advisories/GHSA-hrqr-hxpp-chr3
Type: github-advisory

## Affected
- RubyGems: `rack` — affected >=0 <1.6.12
- RubyGems: `rack` — affected >=2.0.0 <2.0.8

## Details
There's a possible information leak / session hijack vulnerability in Rack. Attackers may be able to find and hijack sessions by using timing attacks targeting the session id. Session ids are usually stored and indexed in a database that uses some kind of scheme for speeding up lookups of that session id. By carefully measuring the amount of time it takes to look up a session, an attacker may be able to find a valid session id and hijack the session.

The session id itself may be generated randomly, but the way the session is indexed by the backing store does not use a secure comparison.

### Impact

The session id stored in a cookie is the same id that is used when querying the backing session storage engine.  Most storage mechanisms (for example a database) use some sort of indexing in order to speed up the lookup of that id.  By carefully timing requests and session lookup failures, an attacker may be able to perform a timing attack to determine an existing session id and hijack that session.

## Releases

The 1.6.12 and 2.0.8 releases are available at the normal locations.

### Workarounds

There are no known workarounds.

### Patches

To aid users who aren't able to upgrade immediately we have provided patches for
the two supported release series. They are in git-am format and consist of a
single changeset.

* 1-6-session-timing-attack.patch - Patch for 1.6 series
* 2-0-session-timing-attack.patch - Patch for 2.6 series

### Credits

Thanks Will Leinweber for reporting this!

## References
- https://github.com/rack/rack/security/advisories/GHSA-hrqr-hxpp-chr3
- https://nvd.nist.gov/vuln/detail/CVE-2019-16782
- https://github.com/rack/rack/commit/7fecaee81f59926b6e1913511c90650e76673b38
- https://github.com/rack/rack
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/rack/CVE-2019-16782.yml
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/HZXMWILCICQLA2BYSP6I2CRMUG53YBLX
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/HZXMWILCICQLA2BYSP6I2CRMUG53YBLX
- http://lists.opensuse.org/opensuse-security-announce/2020-02/msg00016.html
- http://www.openwall.com/lists/oss-security/2019/12/18/2
- http://www.openwall.com/lists/oss-security/2019/12/18/3
- http://www.openwall.com/lists/oss-security/2019/12/19/3
- http://www.openwall.com/lists/oss-security/2020/04/08/1
- http://www.openwall.com/lists/oss-security/2020/04/09/2
