# [H] CVE-2016-10140

## Summary
Severity: High
Advisory: CVE-2016-10140
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2017-01-13
Source: https://osv.dev/vulnerability/CVE-2016-10140
Type: osv

## Details
Information disclosure and authentication bypass vulnerability exists in the Apache HTTP Server configuration bundled with ZoneMinder v1.30 and v1.29, which allows a remote unauthenticated attacker to browse all directories in the web root, e.g., a remote unauthenticated attacker can view all CCTV images on the server via the /events URI.

## References
- http://seclists.org/bugtraq/2017/Feb/6
- http://seclists.org/fulldisclosure/2017/Feb/11
- http://www.securityfocus.com/bid/96849
- https://github.com/ZoneMinder/ZoneMinder/pull/1697
- https://github.com/ZoneMinder/ZoneMinder/commit/71898df7565ed2a51dfe76a1cf30ddb81fc888ba
