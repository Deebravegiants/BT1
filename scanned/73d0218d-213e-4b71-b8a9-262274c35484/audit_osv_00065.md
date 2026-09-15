# [H] ALPINE-CVE-2016-1238

## Summary
Severity: High
Advisory: ALPINE-CVE-2016-1238
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.3, Alpine:v3.4, Alpine:v3.8, Alpine:v3.9
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2016-08-02
Source: https://osv.dev/vulnerability/ALPINE-CVE-2016-1238
Type: osv

## Affected
- Alpine:v3.3: `perl` — affected >=0 <5.22.3-r0
- Alpine:v3.4: `perl` — affected >=0 <5.22.3-r0
- Alpine:v3.10: `spamassassin` — affected >=0 <3.4.2-r0
- Alpine:v3.11: `spamassassin` — affected >=0 <3.4.2-r0
- Alpine:v3.12: `spamassassin` — affected >=0 <3.4.2-r0
- Alpine:v3.13: `spamassassin` — affected >=0 <3.4.2-r0
- Alpine:v3.14: `spamassassin` — affected >=0 <3.4.2-r0
- Alpine:v3.15: `spamassassin` — affected >=0 <3.4.2-r0
- Alpine:v3.16: `spamassassin` — affected >=0 <3.4.2-r0
- Alpine:v3.17: `spamassassin` — affected >=0 <3.4.2-r0
- Alpine:v3.18: `spamassassin` — affected >=0 <3.4.2-r0
- Alpine:v3.19: `spamassassin` — affected >=0 <3.4.2-r0
- Alpine:v3.20: `spamassassin` — affected >=0 <3.4.2-r0
- Alpine:v3.21: `spamassassin` — affected >=0 <3.4.2-r0
- Alpine:v3.22: `spamassassin` — affected >=0 <3.4.2-r0
- Alpine:v3.23: `spamassassin` — affected >=0 <3.4.2-r0
- Alpine:v3.24: `spamassassin` — affected >=0 <3.4.2-r0
- Alpine:v3.8: `spamassassin` — affected >=0 <3.4.3-r0
- Alpine:v3.9: `spamassassin` — affected >=0 <3.4.2-r0

## Details
(1) cpan/Archive-Tar/bin/ptar, (2) cpan/Archive-Tar/bin/ptardiff, (3) cpan/Archive-Tar/bin/ptargrep, (4) cpan/CPAN/scripts/cpan, (5) cpan/Digest-SHA/shasum, (6) cpan/Encode/bin/enc2xs, (7) cpan/Encode/bin/encguess, (8) cpan/Encode/bin/piconv, (9) cpan/Encode/bin/ucmlint, (10) cpan/Encode/bin/unidump, (11) cpan/ExtUtils-MakeMaker/bin/instmodsh, (12) cpan/IO-Compress/bin/zipdetails, (13) cpan/JSON-PP/bin/json_pp, (14) cpan/Test-Harness/bin/prove, (15) dist/ExtUtils-ParseXS/lib/ExtUtils/xsubpp, (16) dist/Module-CoreList/corelist, (17) ext/Pod-Html/bin/pod2html, (18) utils/c2ph.PL, (19) utils/h2ph.PL, (20) utils/h2xs.PL, (21) utils/libnetcfg.PL, (22) utils/perlbug.PL, (23) utils/perldoc.PL, (24) utils/perlivp.PL, and (25) utils/splain.PL in Perl 5.x before 5.22.3-RC2 and 5.24 before 5.24.1-RC2 do not properly remove . (period) characters from the end of the includes directory array, which might allow local users to gain privileges via a Trojan horse module under the current working directory.

## References
- https://security.alpinelinux.org/vuln/CVE-2016-1238
