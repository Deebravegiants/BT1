# [H] CVE-2017-12425

## Summary
Severity: High
Advisory: CVE-2017-12425
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-08-04
Source: https://osv.dev/vulnerability/CVE-2017-12425
Type: osv

## Details
An issue was discovered in Varnish HTTP Cache 4.0.1 through 4.0.4, 4.1.0 through 4.1.7, 5.0.0, and 5.1.0 through 5.1.2. A wrong if statement in the varnishd source code means that particular invalid requests from the client can trigger an assert, related to an Integer Overflow. This causes the varnishd worker process to abort and restart, losing the cached contents in the process. An attacker can therefore crash the varnishd worker process on demand and effectively keep it from serving content - a Denial-of-Service attack. The specific source-code filename containing the incorrect statement varies across releases.

## References
- http://www.debian.org/security/2017/dsa-3924
- https://github.com/varnishcache/varnish-cache/issues/2379
- https://lists.debian.org/debian-security-announce/2017/msg00186.html
- https://www.varnish-cache.org/security/VSV00001.html#vsv00001
- https://bugzilla.redhat.com/show_bug.cgi?id=1477222
- https://bugzilla.suse.com/show_bug.cgi?id=1051917
