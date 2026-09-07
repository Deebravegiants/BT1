# [M] Potential XSS vulnerability in jQuery

## Summary
Severity: Medium
Advisory: GHSA-gxr4-xjj5-5px2
CVE: CVE-2020-11022
CWE: CWE-79
Ecosystem: Maven, NuGet, Packagist, RubyGems, npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:C/C:H/I:L/A:N (CVSS_V3)
Published: 2020-04-29
Source: https://github.com/advisories/GHSA-gxr4-xjj5-5px2
Type: github-advisory

## Affected
- npm: `jquery` — affected >=1.12.0 <3.5.0
- NuGet: `jquery` — affected >=1.12.0 <3.5.0
- RubyGems: `jquery-rails` — affected >=0 <4.4.0
- Maven: `org.webjars.npm:jquery` — affected >=1.12.0 <3.5.0
- Packagist: `maximebf/debugbar` — affected >=0 <1.19.0
- Packagist: `athlon1600/youtube-downloader` — affected >=0 <4.0.1
- Packagist: `components/jquery` — affected >=1.12.0 <3.5.0

## Details
### Impact
Passing HTML from untrusted sources - even after sanitizing it - to one of jQuery's DOM manipulation methods (i.e. `.html()`, `.append()`, and others) may execute untrusted code.

### Patches
This problem is patched in jQuery 3.5.0.

### Workarounds
To workaround the issue without upgrading, adding the following to your code:

```js
jQuery.htmlPrefilter = function( html ) {
	return html;
};
```

You need to use at least jQuery 1.12/2.2 or newer to be able to apply this workaround.

### References
https://blog.jquery.com/2020/04/10/jquery-3-5-0-released/
https://jquery.com/upgrade-guide/3.5/

### For more information
If you have any questions or comments about this advisory, search for a relevant issue in [the jQuery repo](https://github.com/jquery/jquery/issues). If you don't find an answer, open a new issue.

## References
- https://github.com/jquery/jquery/security/advisories/GHSA-gxr4-xjj5-5px2
- https://nvd.nist.gov/vuln/detail/CVE-2020-11022
- https://github.com/maximebf/php-debugbar/issues/447
- https://github.com/jquery/jquery/commit/1d61fd9407e6fbe82fe55cb0b938307aa0791f77
- https://github.com/maximebf/php-debugbar/commit/847216e60544258c881f2733d699bbcfeefac0fc
- https://blog.jquery.com/2020/04/10/jquery-3-5-0-released
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/VOE7P7APPRQKD4FGNHBKJPDY6FFCOH3W
- https://lists.opensuse.org/opensuse-security-announce/2020-07/msg00067.html
- https://lists.opensuse.org/opensuse-security-announce/2020-07/msg00085.html
- https://lists.opensuse.org/opensuse-security-announce/2020-11/msg00039.html
- https://packetstormsecurity.com/files/162159/jQuery-1.2-Cross-Site-Scripting.html
- https://security.gentoo.org/glsa/202007-03
- https://www.debian.org/security/2020/dsa-4693
- https://www.drupal.org/sa-core-2020-002
- https://www.oracle.com//security-alerts/cpujul2021.html
- https://www.oracle.com/security-alerts/cpuApr2021.html
- https://www.oracle.com/security-alerts/cpuapr2022.html
- https://www.oracle.com/security-alerts/cpujan2021.html
- https://www.oracle.com/security-alerts/cpujan2022.html
- https://www.oracle.com/security-alerts/cpujul2020.html
