# [C] DBD::Pg version 3.21.0 for Perl has a heap out-of-bounds write in quote_float

## Summary
Severity: Critical
Advisory: CVE-2026-78183
Aliases: GHSA-785p-fw3v-r822
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-23
Source: https://osv.dev/vulnerability/CVE-2026-78183
Type: osv

## Details
DBD::Pg version 3.21.0 for Perl has a heap out-of-bounds write in quote_float.

quote_float() allocates the length of the string + 1, which is the size of the bare numeric symbol plus NULL.  But for special literals NaN, Inf, +Inf, -Inf, Infinity, +Infinity, -Infinity it emits the literal surrounded by quotes plus NULL, which is length + 3 bytes. Every recognised literal (case-insensitive) overflows by 2 bytes, a single quote and a NULL.

This can be reached by the $dbh->quote method, for example

    $dbh->quote( "Infinity", DBI::SQL_NUMERIC ).

This regression was introduced in 3.21.0 by the quote.c rewrite.

## References
- http://www.openwall.com/lists/oss-security/2026/08/23/5
- https://cpan.org/modules
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/78xxx/CVE-2026-78183.json
- https://github.com/bucardo/dbdpg/security/advisories/GHSA-785p-fw3v-r822
- https://metacpan.org/release/TURNSTEP/DBD-Pg-3.21.1/source/Changes
- https://nvd.nist.gov/vuln/detail/CVE-2026-78183
- https://github.com/bucardo/dbdpg/commit/6d6f47ed2403cda55c82b1bad56e388ba7390065.patch
- https://github.com/bucardo/dbdpg/commit/adacf1de872326a465e13f9e4281a674ebcd227e
- https://github.com/bucardo/dbdpg
