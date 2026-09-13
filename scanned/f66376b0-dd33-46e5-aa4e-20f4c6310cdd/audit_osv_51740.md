# [M] CVE-2021-38507

## Summary
Severity: Medium
Advisory: CVE-2021-38507
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:N)
Published: 2021-12-08
Source: https://osv.dev/vulnerability/CVE-2021-38507
Type: osv

## Details
The Opportunistic Encryption feature of HTTP2 (RFC 8164) allows a connection to be transparently upgraded to TLS while retaining the visual properties of an HTTP connection, including being same-origin with unencrypted connections on port 80. However, if a second encrypted port on the same IP address (e.g. port 8443) did not opt-in to opportunistic encryption; a network attacker could forward a connection from the browser to port 443 to port 8443, causing the browser to treat the content of port 8443 as same-origin with HTTP. This was resolved by disabling the Opportunistic Encryption feature, which had low usage. This vulnerability affects Firefox < 94, Thunderbird < 91.3, and Firefox ESR < 91.3.

## References
- https://lists.debian.org/debian-lts-announce/2021/12/msg00030.html
- https://security.gentoo.org/glsa/202202-03
- https://security.gentoo.org/glsa/202208-14
- https://www.debian.org/security/2021/dsa-5026
- https://www.debian.org/security/2022/dsa-5034
- https://www.mozilla.org/security/advisories/mfsa2021-48/
- https://lists.debian.org/debian-lts-announce/2022/01/msg00001.html
- https://www.mozilla.org/security/advisories/mfsa2021-49/
- https://www.mozilla.org/security/advisories/mfsa2021-50/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1730935
