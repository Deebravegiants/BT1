# [M] CVE-2021-35525

## Summary
Severity: Medium
Advisory: CVE-2021-35525
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2021-06-28
Source: https://osv.dev/vulnerability/CVE-2021-35525
Type: osv

## Details
PostSRSd before 1.11 allows a denial of service (subprocess hang) if Postfix sends certain long data fields such as multiple concatenated email addresses. NOTE: the PostSRSd maintainer acknowledges "theoretically, this error should never occur ... I'm not sure if there's a reliable way to trigger this condition by an external attacker, but it is a security bug in PostSRSd nevertheless."

## References
- https://github.com/roehling/postsrsd/releases/tag/1.11
- https://security.gentoo.org/glsa/202107-08
- https://bugs.gentoo.org/793674
- https://github.com/roehling/postsrsd/commit/077be98d8c8a9847e4ae0c7dc09e7474cbe27db2
