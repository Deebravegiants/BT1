# [H] CVE-2021-21381

## Summary
Severity: High
Advisory: CVE-2021-21381
Aliases: GHSA-xgh4-387p-hqpp
CVSS: 8.2 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:N)
Published: 2021-03-11
Source: https://osv.dev/vulnerability/CVE-2021-21381
Type: osv

## Details
Flatpak is a system for building, distributing, and running sandboxed desktop applications on Linux. In Flatpack since version 0.9.4 and before version 1.10.2 has a vulnerability in the "file forwarding" feature which can be used by an attacker to gain access to files that would not ordinarily be allowed by the app's permissions. By putting the special tokens `@@` and/or `@@u` in the Exec field of a Flatpak app's .desktop file, a malicious app publisher can trick flatpak into behaving as though the user had chosen to open a target file with their Flatpak app, which automatically makes that file available to the Flatpak app. This is fixed in version 1.10.2. A minimal solution is the first commit "`Disallow @@ and @@U usage in desktop files`". The follow-up commits "`dir: Reserve the whole @@ prefix`" and "`dir: Refuse to export .desktop files with suspicious uses of @@ tokens`" are recommended, but not strictly required. As a workaround, avoid installing Flatpak apps from untrusted sources, or check the contents of the exported `.desktop` files in `exports/share/applications/*.desktop` (typically `~/.local/share/flatpak/exports/share/applications/*.desktop` and `/var/lib/flatpak/exports/share/applications/*.desktop`) to make sure that literal filenames do not follow `@@` or `@@u`.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/2MXXLXC2DPJ45HSMTI5MZYHMYEGQN6AA/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/WXNVFOIB6ZP4DGOVKAM25T6OIEP3YLGV/
- https://github.com/flatpak/flatpak/releases/tag/1.10.2
- https://github.com/flatpak/flatpak/security/advisories/GHSA-xgh4-387p-hqpp
- https://security.gentoo.org/glsa/202312-12
- https://www.debian.org/security/2021/dsa-4868
- https://github.com/flatpak/flatpak/commit/8279c5818425b6812523e3805bbe242fb6a5d961
- https://github.com/flatpak/flatpak/commit/a7401e638bf0c03102039e216ab1081922f140ae
- https://github.com/flatpak/flatpak/commit/eb7946bb6248923d8c90fe9b84425fef97ae580d
- https://github.com/flatpak/flatpak/pull/4156
