# [M] WWW::Mechanize::Cached versions before 2.00 for Perl deserialize cached HTTP responses from a world-writable on-disk cache, enabling local response forgery and code execution

## Summary
Severity: Medium
Advisory: CVE-2026-8612
CVSS: 5.3 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L)
Published: 2026-05-15
Source: https://osv.dev/vulnerability/CVE-2026-8612
Type: osv

## Details
WWW::Mechanize::Cached versions before 2.00 for Perl deserialize cached HTTP responses from a world-writable on-disk cache, enabling local response forgery and code execution.

With no explicit cache backend, WWW::Mechanize::Cached constructs a default Cache::FileCache under /tmp/FileCache without overriding the backend's documented directory_umask of 000, so the cache root and its subdirectories are created mode 0777 with no sticky bit. Cache entries are named by sha1_hex of the request and read back through Storable::thaw on the next cache hit.

A local attacker with write access to the cache tree can replace a victim's cache entry for a known URL with an arbitrary frozen HTTP::Response blob, causing the victim's next get() of that URL to return attacker controlled response bytes. Because the bytes are passed to Storable::thaw, a victim process that has loaded any class with a side-effectful STORABLE_thaw, DESTROY, or overload hook can be escalated to arbitrary code execution.

## References
- http://www.openwall.com/lists/oss-security/2026/05/15/1
- https://cpan.org/modules
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/8xxx/CVE-2026-8612.json
- https://metacpan.org/release/OALDERS/WWW-Mechanize-Cached-2.00/changes
- https://nvd.nist.gov/vuln/detail/CVE-2026-8612
- https://github.com/libwww-perl/WWW-Mechanize-Cached/commit/b821647deeedf83490ebc1db91d959d942300ce0.patch
- https://github.com/libwww-perl/WWW-Mechanize-Cached/pull/36
- https://github.com/libwww-perl/WWW-Mechanize-Cached
