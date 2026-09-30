# [M] CVE-2020-12404

## Summary
Severity: Medium
Advisory: CVE-2020-12404
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:N/A:N)
Published: 2020-07-09
Source: https://osv.dev/vulnerability/CVE-2020-12404
Type: osv

## Details
For native-to-JS bridging the app requires a unique token to be passed that ensures non-app code can't call the bridging functions. That token could leak when used for downloading files. This vulnerability affects Firefox for iOS < 26.

## References
- https://www.mozilla.org/security/advisories/mfsa2020-19/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1631739
