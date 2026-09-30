# [H] CVE-2020-6830

## Summary
Severity: High
Advisory: CVE-2020-6830
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2020-05-26
Source: https://osv.dev/vulnerability/CVE-2020-6830
Type: osv

## Details
For native-to-JS bridging, the app requires a unique token to be passed that ensures non-app code can't call the bridging functions. That token was being used for JS-to-native also, but it isn't needed in this case, and its usage was also leaking this token. This vulnerability affects Firefox for iOS < 25.

## References
- https://www.mozilla.org/security/advisories/mfsa2020-15/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1632387
