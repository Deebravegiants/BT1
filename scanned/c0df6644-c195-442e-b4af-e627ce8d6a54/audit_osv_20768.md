# [H] CVE-2021-36770

## Summary
Severity: High
Advisory: CVE-2021-36770
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2021-08-11
Source: https://osv.dev/vulnerability/CVE-2021-36770
Type: osv

## Details
Encode.pm, as distributed in Perl through 5.34.0, allows local users to gain privileges via a Trojan horse Encode::ConfigLocal library (in the current working directory) that preempts dynamic module loading. Exploitation requires an unusual configuration, and certain 2021 versions of Encode.pm (3.05 through 3.11). This issue occurs because the || operator evaluates @INC in a scalar context, and thus @INC has only an integer value.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/5NDGQSGMEZ75FJGBKNYC75OTO7TF7XHB/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/6KOZYD7BH2DNIAEZ2ZL4PJ4QUVQI6Y33/
- https://metacpan.org/dist/Encode/changes
- https://news.cpanel.com/unscheduled-tsr-10-august-2021/
- https://security-tracker.debian.org/tracker/CVE-2021-36770
- https://security.netapp.com/advisory/ntap-20210909-0003/
- https://security.netapp.com/advisory/ntap-20241108-0002/
- https://github.com/Perl/perl5/commit/c1a937fef07c061600a0078f4cb53fe9c2136bb9
- https://github.com/dankogai/p5-encode/commit/527e482dc70b035d0df4f8c77a00d81f8d775c74
