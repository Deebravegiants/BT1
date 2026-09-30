# [C] BIT-roundcube-2020-12641

## Summary
Severity: Critical
Advisory: BIT-roundcube-2020-12641
Aliases: CVE-2020-12641
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-roundcube-2020-12641
Type: osv

## Affected
- Bitnami: `roundcube` — affected >=1.4.0 <1.4.4

## Details
rcube_image.php in Roundcube Webmail before 1.4.4 allows attackers to execute arbitrary code via shell metacharacters in a configuration setting for im_convert_path or im_identify_path.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-09/msg00083.html
- https://github.com/DrunkenShells/Disclosures/tree/master/CVE-2020-12641-Command%20Injection-Roundcube
- https://github.com/roundcube/roundcubemail/commit/fcfb099477f353373c34c8a65c9035b06b364db3
- https://github.com/roundcube/roundcubemail/compare/1.4.3...1.4.4
- https://github.com/roundcube/roundcubemail/releases/tag/1.4.4
- https://roundcube.net/news/2020/04/29/security-updates-1.4.4-1.3.11-and-1.2.10
- https://security.gentoo.org/glsa/202007-41
