# [H] Meta Box Plugin for WordPress: Authenticated (Contributor+) Arbitrary File Deletion via ajax_delete_file

## Summary
Severity: High
Advisory: GHSA-m4q3-832v-44j6
CVE: CVE-2025-14675
CWE: CWE-22
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-03-07
Source: https://github.com/advisories/GHSA-m4q3-832v-44j6
Type: github-advisory

## Affected
- Packagist: `wpmetabox/meta-box` — affected >=0 <5.11.2

## Details
The Meta Box plugin for WordPress is vulnerable to arbitrary file deletion due to insufficient file path validation in the 'ajax_delete_file' function in all versions up to, and including, 5.11.1. This makes it possible for authenticated attackers, with Contributor-level access and above, to delete arbitrary files on the server, which can easily lead to remote code execution when the right file is deleted (such as wp-config.php).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-14675
- https://github.com/wpmetabox/meta-box/pull/1654
- https://github.com/wpmetabox/meta-box/commit/08c6511607b9cc9fe8d0de7a7e91c9d5d415f831
- https://github.com/wpmetabox/meta-box
- https://plugins.trac.wordpress.org/browser/meta-box/tags/5.11.0/inc/fields/file.php#L30
- https://plugins.trac.wordpress.org/browser/meta-box/tags/5.11.0/inc/fields/file.php#L54
- https://plugins.trac.wordpress.org/changeset/3475210/meta-box#file3
- https://www.wordfence.com/threat-intel/vulnerabilities/id/036467de-95bb-4bfd-9522-df8dc17f3102?source=cve
