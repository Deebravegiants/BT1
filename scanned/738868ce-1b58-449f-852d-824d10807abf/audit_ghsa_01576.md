# [M] receiving subscription objects with deleted session

## Summary
Severity: Medium
Advisory: GHSA-2xm2-xj2q-qgpj
CVE: CVE-2020-15270
CWE: CWE-672
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2020-10-27
Source: https://github.com/advisories/GHSA-2xm2-xj2q-qgpj
Type: github-advisory

## Affected
- npm: `parse-server` — affected >=0 <4.4.0

## Details
Original Message:
Hi,

I create objects with one client with an ACL of all users with a specific column value. Thats working so far.

Then I deleted the session object from one user to look if he can receive subscription objects and he can receive them.
The client with the deleted session cant create new objects, which Parse restricts right.

The LiveQueryServer doesnt detect deleted sessions after the websocket connection was established.
There should be a mechanism that checks in an specific interval if the session exists.
I dont know if its true with expired sessions.

Any solutions?

Parse version: 4.3.0
Parse js SDK version: 2.17

Solution:
Hi guys.

I've found and fixed the problem. It happens because there are two caches in place for the session token:

- at Parse Server level, which, according with the docs, should be changed via cacheTTL option and defaults to 5 seconds;
- at Parse Live Query level, which, according with the docs, should be changed via liveQueryServerOptions.cacheTimeout and defaults to 30 days.

But there are three problems:

- cacheTTL has currently no effect over Live Query Server;
- cacheTimeout also has currently no effect over Live Query Server;
- cacheTimeout actually defaults to 1h.

So, currently, if you wait 1 hour after the session token was invalidated, the clients using the old session token are not able to receive the events.

What I did:

- Added a test case for the problem;
- Fixed cacheTTL for Live Query Server;
- Fixed cacheTimeout for Live Query Server;
- Changed the cacheTimeout to default 5s;
- Changed the docs to reflect the actual 5s default for cacheTimeout.

## References
- https://github.com/parse-community/parse-server/security/advisories/GHSA-2xm2-xj2q-qgpj
- https://nvd.nist.gov/vuln/detail/CVE-2020-15270
- https://github.com/parse-community/parse-server/commit/78b59fb26b1c36e3cdbd42ba9fec025003267f58
- https://github.com/parse-community/parse-server
