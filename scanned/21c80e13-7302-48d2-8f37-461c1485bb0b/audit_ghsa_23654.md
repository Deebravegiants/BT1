# [M] jplayer Cross Site Scripting vulnerability

## Summary
Severity: Medium
Advisory: GHSA-3jcq-cwr7-6332
CVE: CVE-2013-2022
CWE: CWE-79
Ecosystem: npm
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-3jcq-cwr7-6332
Type: github-advisory

## Affected
- npm: `jplayer` — affected >=0 <2.3.0

## Details
Multiple cross-site scripting (XSS) vulnerabilities in actionscript/Jplayer.as in the Flash SWF component (jplayer.swf) in jPlayer before 2.3.0 allow remote attackers to inject arbitrary web script or HTML via the (1) jQuery or (2) id parameters, a different vulnerability than CVE-2013-1942 and CVE-2013-2023, as demonstrated by using the alert function in the jQuery parameter.  NOTE: these are the same parameters as CVE-2013-1942, but the fix for CVE-2013-1942 uses a blacklist for the jQuery parameter.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2013-2022
- https://github.com/happyworm/jPlayer/commit/c5fe17bb4459164bd59153b57248cf94b8867373
- https://github.com/jplayer/jPlayer/commit/c5fe17bb4459164bd59153b57248cf94b8867373
- https://github.com/jplayer/jPlayer
- http://marc.info/?l=oss-security&m=136570964825921&w=2
- http://marc.info/?l=oss-security&m=136726705917858&w=2
- http://marc.info/?l=oss-security&m=136773622321563&w=2
- http://seclists.org/fulldisclosure/2013/Apr/192
- http://www.jplayer.org/2.3.0/release-notes
- http://www.openwall.com/lists/oss-security/2013/06/27/7
- http://www.openwall.com/lists/oss-security/2013/07/04/5
