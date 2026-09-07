# [M] Cross-Site Scripting (XSS) in jquery

## Summary
Severity: Medium
Advisory: GHSA-rmxg-73gg-4p98
CVE: CVE-2015-9251
CWE: CWE-79
Ecosystem: Maven, NuGet, RubyGems, npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2018-01-22
Source: https://github.com/advisories/GHSA-rmxg-73gg-4p98
Type: github-advisory

## Affected
- npm: `jquery` — affected >=0 <1.12.2
- NuGet: `jQuery` — affected >=0 <1.12.2
- NuGet: `jQuery` — affected >=1.12.3 <3.0.0
- npm: `jquery` — affected >=1.12.3 <3.0.0
- RubyGems: `jquery-rails` — affected >=0 <4.2.0
- Maven: `org.webjars.npm:jquery` — affected >=0 <1.12.2
- Maven: `org.webjars.npm:jquery` — affected >=1.12.3 <3.0.0

## Details
Affected versions of `jquery` interpret `text/javascript` responses from cross-origin ajax requests, and automatically execute the contents in `jQuery.globalEval`, even when the ajax request doesn't contain the `dataType` option.


## Recommendation

Update to version 3.0.0 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-9251
- https://github.com/jquery/jquery/issues/2432
- https://github.com/jquery/jquery/issues/2432#issuecomment-403761229
- https://github.com/jquery/jquery/pull/2588
- https://github.com/jquery/jquery/pull/2588/commits/c254d308a7d3f1eac4d0b42837804cfffcba4bb2
- https://github.com/jquery/jquery/commit/b078a62013782c7424a4a61a240c23c4c0b42614
- https://github.com/jquery/jquery/commit/f60729f3903d17917dc351f3ac87794de379b0cc
- https://access.redhat.com/errata/RHSA-2020:0481
- https://seclists.org/bugtraq/2019/May/18
- https://security.netapp.com/advisory/ntap-20210108-0004
- https://security.snyk.io/vuln/SNYK-DOTNET-JQUERY-450227
- https://snyk.io/vuln/npm:jquery:20150627
- https://sw.aveva.com/hubfs/assets-2018/pdf/security-bulletin/SecurityBulletin_LFSec126.pdf
- https://web.archive.org/web/20200227030101/http://www.securityfocus.com/bid/105658
- https://www.oracle.com/security-alerts/cpuapr2020.html
- https://www.oracle.com/security-alerts/cpujan2020.html
- https://www.oracle.com/security-alerts/cpujul2020.html
- https://www.oracle.com/security-alerts/cpuoct2020.html
- https://www.oracle.com/technetwork/security-advisory/cpuapr2019-5072813.html
- https://www.oracle.com/technetwork/security-advisory/cpujan2019-5072801.html
