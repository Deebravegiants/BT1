# [M] net-imap vulnerable to command Injection via unvalidated Symbol inputs

## Summary
Severity: Medium
Advisory: GHSA-75xq-5h9v-w6px
CVE: CVE-2026-42258
CWE: CWE-77, CWE-93
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:H/A:L (CVSS_V3)
Published: 2026-05-04
Source: https://github.com/advisories/GHSA-75xq-5h9v-w6px
Type: github-advisory

## Affected
- RubyGems: `net-imap` — affected >=0.6.0 <0.6.4
- RubyGems: `net-imap` — affected >=0.5.0 <0.5.14
- RubyGems: `net-imap` — affected >=0 <0.4.24

## Details
### Summary

Symbol arguments to commands are vulnerable to a CRLF Injection / IMAP Command injection via Symbol arguments passed to IMAP commands.

### Details

Symbol arguments represent IMAP "system flags", which are formatted as "atoms" (with no quoting) with a `"\"` prefix.  Vulnerable versions of Net::IMAP sends the symbol name directly to the socket, with no validation.

Because the Symbol input is unvalidated, it could contain invalid `flag` characters, including `SP` and `CRLF`, which could be used to finish the current command and inject new commands.

Although IMAP `flag` arguments are only valid input for a few IMAP commands, most Net::IMAP commands use generic argument handling, and will allow Symbol (`flag`) inputs.

Note also that the list of valid symbol inputs should be restricted to an enumerated set of standard RFC defined flag types, which have each been given specific defined semantics.  Any user-provided values outside of that list of standard "system flags" needs to use the IMAP `keyword` syntax, which are sent as atoms, i.e: string inputs. Under no circumstances should `#to_sym` ever be called on unvetted user-provided input: that will always be a bug in the calling code for the simple reason that `user_input_atom` is  as `\user_input_atom`.

For forward compatibility with future IMAP extentions, Net::IMAP, does not restrict flag inputs to an enumerated list.  That is the responsibility of the calling application code, which knows which flag semantics are valid for its context.

### Impact

If a developer passes user-controlled input as a Symbol to most Net::IMAP commands, an attacker can append CRLF sequence followed by a new IMAP command (like `DELETE mailbox`).

### Mitigation
* Upgrade to a version of Net::IMAP that validates Symbols are valid as an IMAP `flag`.
* User-provided input should never be able to control calling `#to_sym` on string arguments.

  For example, do not unsafely serialize and deserialize command arguments (e.g. with YAML or Marshal) in a way that could create unvetted Symbol arguments.
* For the few IMAP commands which do allow `flag` arguments, it may be appropriate to hard-code Symbol arguments or restrict them to an enumerated list which is valid for the calling application.

## References
- https://github.com/ruby/net-imap/security/advisories/GHSA-75xq-5h9v-w6px
- https://nvd.nist.gov/vuln/detail/CVE-2026-42258
- https://github.com/ruby/net-imap/commit/aec06996eb87a7e1bbcef1f9f8926e8add2b8c71
- https://github.com/ruby/net-imap/commit/9db3e9d60bfb8f3735ea95015bf8a700f4af9cbb
- https://github.com/ruby/net-imap/commit/6bf02aef7e0b5931010c36e377f79a71636b306b
- https://access.redhat.com/errata/RHSA-2026:33462
- https://access.redhat.com/errata/RHSA-2026:37238
- https://access.redhat.com/errata/RHSA-2026:37397
- https://access.redhat.com/errata/RHSA-2026:38694
- https://access.redhat.com/errata/RHSA-2026:40380
- https://access.redhat.com/security/cve/CVE-2026-42258
- https://bugzilla.redhat.com/show_bug.cgi?id=2468498
- https://github.com/ruby/net-imap
- https://github.com/ruby/net-imap/releases/tag/v0.4.24
- https://github.com/ruby/net-imap/releases/tag/v0.5.14
- https://github.com/ruby/net-imap/releases/tag/v0.6.4
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/net-imap/CVE-2026-42258.yml
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-42258.json
- https://access.redhat.com/errata/RHSA-2026:33512
- https://access.redhat.com/errata/RHSA-2026:33514
