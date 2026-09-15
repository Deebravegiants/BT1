# [H] XNIO `notifyReadClosed` method logging message to unexpected end

## Summary
Severity: High
Advisory: GHSA-76fg-mhrg-fmmg
CVE: CVE-2022-0084
CWE: CWE-770
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-08-27
Source: https://github.com/advisories/GHSA-76fg-mhrg-fmmg
Type: github-advisory

## Affected
- Maven: `org.jboss.xnio:xnio-all` — affected >=0

## Details
A flaw was found in XNIO, specifically in the `notifyReadClosed` method. The issue revealed this method was logging a message to another expected end. This flaw allows an attacker to send flawed requests to a server, possibly causing log contention-related performance concerns or an unwanted disk fill-up. A fix for this issue is available on the `3.x` branch of the repository.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-0084
- https://github.com/xnio/xnio/pull/291
- https://github.com/xnio/xnio/commit/fdefb3b8b715d33387cadc4d48991fb1989b0c12
- https://access.redhat.com/security/cve/CVE-2022-0084
- https://bugzilla.redhat.com/show_bug.cgi?id=2064226
- https://github.com/xnio/xnio
