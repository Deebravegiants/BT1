# [M] JLSEC-2026-512

## Summary
Severity: Medium
Advisory: JLSEC-2026-512
Ecosystem: Julia
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-05-19
Source: https://osv.dev/vulnerability/JLSEC-2026-512
Type: osv

## Affected
- Julia: `Librsvg_jll` — affected >=2.52.4+0 <2.54.7+0

## Details
A directory traversal problem in the URL decoder of librsvg before 2.56.3 could be used by local or remote attackers to disclose files (on the local filesystem outside of the expected area), as demonstrated by `href=".?../../../../../../../../../../etc/passwd"` in an `xi:include` element.

## References
- http://seclists.org/fulldisclosure/2023/Jul/43
- http://www.openwall.com/lists/oss-security/2023/07/27/1
- http://www.openwall.com/lists/oss-security/2023/09/06/10
- https://bugzilla.suse.com/show_bug.cgi?id=1213502
- https://gitlab.gnome.org/GNOME/librsvg/-/issues/996
- https://gitlab.gnome.org/GNOME/librsvg/-/releases/2.56.3
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/422NTIHIEBRASIG2DWXYBH4ADYMHY626/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/R5BCXT5GW6RCL45ZUHUZR4CJG2BAFDVC/
- https://news.ycombinator.com/item?id=37415799
- https://security.netapp.com/advisory/ntap-20230831-0011/
- https://www.canva.dev/blog/engineering/when-url-parsers-disagree-cve-2023-38633/
- https://www.debian.org/security/2023/dsa-5484
