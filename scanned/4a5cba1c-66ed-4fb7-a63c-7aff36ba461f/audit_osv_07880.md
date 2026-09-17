# [H] IDNA 2003 makes curl use wrong host

## Summary
Severity: High
Advisory: CURL-CVE-2016-8625
Aliases: CVE-2016-8625
Published: 2016-11-02
Source: https://osv.dev/vulnerability/CURL-CVE-2016-8625
Type: osv

## Details
When curl is built with libidn to handle International Domain Names (IDNA), it
translates them to puny code for DNS resolving using the IDNA 2003 standard,
while IDNA 2008 is the modern and up-to-date IDNA standard.

This misalignment causes problems with for example domains using the German ß
character (known as the Unicode Character `LATIN SMALL LETTER SHARP S`) which
is used at times in the `.de` TLD and is translated differently in the two
IDNA standards, leading to users potentially and unknowingly issuing network
transfer requests to the wrong host.

For example, `straße.de` is translated into `strasse.de` using IDNA 2003 but
is translated into `xn--strae-oqa.de` using IDNA 2008. Needless to say, those
hostnames could well resolve to different addresses and be two completely
independent servers. IDNA 2008 is mandatory for `.de` domains.

curl is not alone with this problem, as there is currently a big flux in the
world of network user-agents about which IDNA version to support and use.

This name problem exists for DNS-using protocols in curl, but only when built
to use libidn.
