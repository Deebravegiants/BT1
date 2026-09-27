# [M] Mojo::JSON versions before 9.47 for Perl allow memory exhaustion via unbounded recursion in the pure-Perl decoder

## Summary
Severity: Medium
Advisory: CVE-2026-14803
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-07-06
Source: https://osv.dev/vulnerability/CVE-2026-14803
Type: osv

## Details
Mojo::JSON versions before 9.47 for Perl allow memory exhaustion via unbounded recursion in the pure-Perl decoder.

The pure-Perl decode path (`_decode_value` dispatching to `_decode_array` and `_decode_object`) recurses with no depth limit, so a small deeply nested JSON document can consume excessive memory.

This path is the default when Cpanel::JSON::XS is not installed or `MOJO_NO_JSON_XS=1` is set; the Cpanel::JSON::XS fast path is not affected.

Any caller that decodes an untrusted JSON body, for example `Mojo::Message::json` reached through `$c->req->json`, can exhaust process memory and cause denial of service.

## References
- http://www.openwall.com/lists/oss-security/2026/07/06/2
- https://cpan.org/modules
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/14xxx/CVE-2026-14803.json
- https://metacpan.org/release/SRI/Mojolicious-9.47/changes
- https://nvd.nist.gov/vuln/detail/CVE-2026-14803
- https://github.com/mojolicious/mojo/commit/cc38b0554275c4d84f6b8b49bcbbc1bec2068fe1.patch
- https://github.com/mojolicious/mojo
