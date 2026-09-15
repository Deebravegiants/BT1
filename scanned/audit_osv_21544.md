# [H] CVE-2021-43828

## Summary
Severity: High
Advisory: CVE-2021-43828
Aliases: GHSA-x4wp-xvq7-w5vr
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2021-12-14
Source: https://osv.dev/vulnerability/CVE-2021-43828
Type: osv

## Details
PatrOwl is a free and open-source solution for orchestrating Security Operations. In versions prior to 1.77 an improper privilege management (IDOR) has been found in PatrowlManager. All imports findings file is placed under /media/imports/<owner_id>/<tmp_file> In that, owner_id is predictable and tmp_file is in format of import_<ownder_id>_<time_created>, for example: import_1_1639213059582.json This filename is predictable and allows anyone without logging in to download all finding import files This vulnerability is capable of allowing unlogged in users to download all finding imports file. Users are advised to update to 1.7.7 as soon as possible. There are no known workarounds.

## References
- https://github.com/Patrowl/PatrowlManager/security/advisories/GHSA-x4wp-xvq7-w5vr
- https://huntr.dev/bounties/fe6248f1-603d-43df-816c-c75534a56f72
