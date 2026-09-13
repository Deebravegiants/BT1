# [C] Concierge::Sessions versions from 0.8.1 before 0.8.5 for Perl generate insecure session ids

## Summary
Severity: Critical
Advisory: CVE-2026-2439
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-02-16
Source: https://osv.dev/vulnerability/CVE-2026-2439
Type: osv

## Details
Concierge::Sessions versions from 0.8.1 before 0.8.5 for Perl generate insecure session ids. The generate_session_id function in Concierge::Sessions::Base defaults to using the uuidgen command to generate a UUID, with a fallback to using Perl's built-in rand function. Neither of these methods are secure, and attackers are able to guess session_ids that can grant them access to systems. Specifically,

  *  There is no warning when uuidgen fails. The software can be quietly using the fallback rand() function with no warnings if the command fails for any reason.
  *  The uuidgen command will generate a time-based UUID if the system does not have a high-quality random number source, because the call does not explicitly specify the --random option. Note that the system time is shared in HTTP responses.
  *  UUIDs are identifiers whose mere possession grants access, as per RFC 9562.
  *  The output of the built-in rand() function is predictable and unsuitable for security applications.

## References
- https://cpan.org/modules
- https://metacpan.org/release/BVA/Concierge-Sessions-v0.8.4/diff/BVA/Concierge-Sessions-v0.8.5#lib/Concierge/Sessions/Base.pm
- https://perldoc.perl.org/5.42.0/functions/rand
- https://security.metacpan.org/docs/guides/random-data-for-security.html
- https://www.rfc-editor.org/rfc/rfc9562.html#name-security-considerations
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/2xxx/CVE-2026-2439.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-2439
- https://github.com/bwva/Concierge-Sessions/commit/20bb28e92e8fba307c4ff8264701c215be65e73b
- https://github.com/bwva/Concierge-Sessions
