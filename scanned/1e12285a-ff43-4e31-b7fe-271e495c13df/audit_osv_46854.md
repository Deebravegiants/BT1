# [C] CVE-2015-6764

## Summary
Severity: Critical
Advisory: CVE-2015-6764
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2015-12-06
Source: https://osv.dev/vulnerability/CVE-2015-6764
Type: osv

## Details
The BasicJsonStringifier::SerializeJSArray function in json-stringifier.h in the JSON stringifier in Google V8, as used in Google Chrome before 47.0.2526.73, improperly loads array elements, which allows remote attackers to cause a denial of service (out-of-bounds memory access) or possibly have unspecified other impact via crafted JavaScript code.

## References
- http://www.debian.org/security/2015/dsa-3415
- https://security.gentoo.org/glsa/201603-09
- http://googlechromereleases.blogspot.com/2015/12/stable-channel-update.html
- http://lists.opensuse.org/opensuse-security-announce/2015-12/msg00016.html
- http://lists.opensuse.org/opensuse-security-announce/2015-12/msg00017.html
- http://lists.opensuse.org/opensuse-updates/2016-01/msg00045.html
- http://www.securityfocus.com/bid/78209
- http://www.securitytracker.com/id/1034298
- https://chromium.googlesource.com/v8/v8/+/6df9a1db8c85ab63dee63879456b6027df53fabc
- https://code.google.com/p/chromium/issues/detail?id=554946
- https://codereview.chromium.org/1440223002
