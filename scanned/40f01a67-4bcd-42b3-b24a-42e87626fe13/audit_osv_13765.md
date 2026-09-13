# [M] CVE-2018-25160

## Summary
Severity: Medium
Advisory: CVE-2018-25160
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N)
Published: 2026-02-27
Source: https://osv.dev/vulnerability/CVE-2018-25160
Type: osv

## Details
HTTP::Session2 versions through 1.09 for Perl does not validate the format of user provided session ids, enabling code injection or other impact depending on session backend.

For example, if an application uses memcached for session storage, then it may be possible for a remote attacker to inject memcached commands in the session id value.

## References
- http://www.openwall.com/lists/oss-security/2026/02/27/13
- https://metacpan.org/pod/Cache::Memcached::Fast::Safe
- https://metacpan.org/release/TOKUHIROM/HTTP-Session2-1.10/source/Changes
- https://github.com/tokuhirom/HTTP-Session2/commit/813838f6d08034b6a265a70e53b59b941b5d3e6d.patch
