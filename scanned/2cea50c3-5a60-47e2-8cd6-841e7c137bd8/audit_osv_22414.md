# [H] ReDoS on endpoint html5client/useragent in BigBlueButton

## Summary
Severity: High
Advisory: CVE-2022-29169
Aliases: GHSA-rwrv-p665-4vwp
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-06-01
Source: https://osv.dev/vulnerability/CVE-2022-29169
Type: osv

## Details
BigBlueButton is an open source web conferencing system. Versions starting with 2.2 and prior to 2.3.19, 2.4.7, and 2.5.0-beta.2 are vulnerable to regular expression denial of service (ReDoS) attacks. By using specific a RegularExpression, an attacker can cause denial of service for the bbb-html5 service. The useragent library performs checking of device by parsing the input of User-Agent header and lets it go through lookupUserAgent() (alias of useragent.lookup() ). This function handles input by regexing and attackers can abuse that by providing some ReDos payload using `SmartWatch`. The maintainers removed `htmlclient/useragent` from versions 2.3.19, 2.4.7, and 2.5.0-beta.2. As a workaround, disable NginX forwarding the requests to the handler according to the directions in the GitHub Security Advisory.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/29xxx/CVE-2022-29169.json
- https://github.com/bigbluebutton/bigbluebutton/security/advisories/GHSA-rwrv-p665-4vwp
- https://nvd.nist.gov/vuln/detail/CVE-2022-29169
- https://github.com/bigbluebutton/bigbluebutton/pull/14886
- https://github.com/bigbluebutton/bigbluebutton/pull/14896
