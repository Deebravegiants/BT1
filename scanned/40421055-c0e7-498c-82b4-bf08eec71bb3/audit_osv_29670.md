# [M] MySQL & free URL mode allows to hide existing notes in hedgedoc

## Summary
Severity: Medium
Advisory: CVE-2024-45308
Aliases: GHSA-pjf2-269h-cx7p
CVSS: 6.5 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:L)
Published: 2024-09-02
Source: https://osv.dev/vulnerability/CVE-2024-45308
Type: osv

## Details
HedgeDoc is an open source, real-time, collaborative, markdown notes application. When using HedgeDoc 1 with MySQL or MariaDB, it is possible to create notes with an alias matching the ID of existing notes. The affected existing note can then not be accessed anymore and is effectively hidden by the new one. When the freeURL feature is enabled (by setting the `allowFreeURL` config option or the `CMD_ALLOW_FREEURL` environment variable to `true`), any user with the appropriate permissions can create a note with an arbitrary alias, e.g. by accessing it in the browser. When MySQL or MariaDB are used, it is possible to create a new note with an alias that matches the lower-cased ID of a different note. HedgeDoc then always presents the new note to users, as these databases perform case-insensitive matching and the lower-cased alias is found first. This issue only affects HedgeDoc instances that use MySQL or MariaDB. Depending on the permission settings of the HedgeDoc instance, the issue can be exploited only by logged-in users or by all (including non-logged-in) users. The exploit requires knowledge of the ID of the target note. Attackers could use this issue to present a manipulated copy of the original note to the user, e.g. by replacing the links with malicious ones. Attackers can also use this issue to prevent access to the original note, causing a denial of service. No data is lost, as the original content of the affected notes is still present in the database. Users are advised to upgrade to version 1.10.0 which addresses this issue. Users unable to upgrade may disable freeURL mode which prevents the exploitation of this issue. The impact can also be limited by restricting freeURL note creation to trusted, logged-in users by enabling `requireFreeURLAuthentication`/`CMD_REQUIRE_FREEURL_AUTHENTICATION`.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/45xxx/CVE-2024-45308.json
- https://github.com/hedgedoc/hedgedoc/security/advisories/GHSA-pjf2-269h-cx7p
- https://nvd.nist.gov/vuln/detail/CVE-2024-45308
- https://github.com/hedgedoc/hedgedoc/commit/380587b7fd65bc1eb71eef51a3aab324f9877650
