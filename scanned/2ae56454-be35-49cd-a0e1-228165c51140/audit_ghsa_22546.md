# [M] Cross-site scripting vulnerability in includes/actions/InfoAction.php

## Summary
Severity: Medium
Advisory: GHSA-6h86-9r5g-f2h5
CVE: CVE-2014-2853
CWE: CWE-79
Ecosystem: Packagist
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-6h86-9r5g-f2h5
Type: github-advisory

## Affected
- Packagist: `mediawiki/core` — affected >=0 <1.21.9
- Packagist: `mediawiki/core` — affected >=1.22.0 <1.22.6

## Details
Cross-site scripting (XSS) vulnerability in includes/actions/InfoAction.php in MediaWiki before 1.21.9 and 1.22.x before 1.22.6 allows remote attackers to inject arbitrary web script or HTML via the sort key in an info action.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-2853
- https://github.com/wikimedia/mediawiki-core/commit/0b695ae09aada343ab59be4a3c9963995a1143b6
- https://bugzilla.redhat.com/show_bug.cgi?id=1091967
- https://bugzilla.wikimedia.org/show_bug.cgi?id=63251
- https://github.com/wikimedia/mediawiki
- https://www.mediawiki.org/wiki/Release_notes/1.21#Changes_since_1.21.8
- https://www.mediawiki.org/wiki/Release_notes/1.22#Changes_since_1.22.5
- http://lists.wikimedia.org/pipermail/mediawiki-announce/2014-April/000149.html
- http://secunia.com/advisories/58262
- http://www.securityfocus.com/bid/67068
- http://www.securitytracker.com/id/1030161
