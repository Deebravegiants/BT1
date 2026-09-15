# [H] CVE-2021-43539

## Summary
Severity: High
Advisory: CVE-2021-43539
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2021-12-08
Source: https://osv.dev/vulnerability/CVE-2021-43539
Type: osv

## Details
Failure to correctly record the location of live pointers across wasm instance calls resulted in a GC occurring within the call not tracing those live pointers. This could have led to a use-after-free causing a potentially exploitable crash. This vulnerability affects Thunderbird < 91.4.0, Firefox ESR < 91.4.0, and Firefox < 95.

## References
- https://lists.debian.org/debian-lts-announce/2022/01/msg00001.html
- https://security.gentoo.org/glsa/202202-03
- https://security.gentoo.org/glsa/202208-14
- https://www.debian.org/security/2021/dsa-5026
- https://www.debian.org/security/2022/dsa-5034
- https://www.mozilla.org/security/advisories/mfsa2021-52/
- https://www.mozilla.org/security/advisories/mfsa2021-53/
- https://lists.debian.org/debian-lts-announce/2021/12/msg00030.html
- https://www.mozilla.org/security/advisories/mfsa2021-54/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1739683
