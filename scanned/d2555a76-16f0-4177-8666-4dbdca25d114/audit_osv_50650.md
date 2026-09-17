# [M] CVE-2020-26976

## Summary
Severity: Medium
Advisory: CVE-2020-26976
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:N)
Published: 2021-01-07
Source: https://osv.dev/vulnerability/CVE-2020-26976
Type: osv

## Details
When a HTTPS pages was embedded in a HTTP page, and there was a service worker registered for the former, the service worker could have intercepted the request for the secure page despite the iframe not being a secure context due to the (insecure) framing. This vulnerability affects Firefox < 84.

## References
- https://security.gentoo.org/glsa/202102-02
- https://www.debian.org/security/2021/dsa-4840
- https://www.debian.org/security/2021/dsa-4842
- https://www.mozilla.org/security/advisories/mfsa2020-54/
- https://lists.debian.org/debian-lts-announce/2021/02/msg00001.html
- https://lists.debian.org/debian-lts-announce/2021/02/msg00002.html
- https://bugzilla.mozilla.org/show_bug.cgi?id=1674343
