# [M] CVE-2021-41233

## Summary
Severity: Medium
Advisory: CVE-2021-41233
Aliases: GHSA-26c8-35cm-xq9m
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2022-03-10
Source: https://osv.dev/vulnerability/CVE-2021-41233
Type: osv

## Details
Nextcloud text is a collaborative document editing using Markdown built for the nextcloud server. Due to an issue with the Nextcloud Text application, which is by default shipped with Nextcloud Server, an attacker is able to access the folder names of "File Drop". For successful exploitation an attacker requires knowledge of the sharing link. It is recommended that users upgrade their Nextcloud Server to 20.0.14, 21.0.6 or 22.2.1. Users unable to upgrade should disable the Nextcloud Text application in the application settings.

## References
- https://github.com/nextcloud/security-advisories/security/advisories/GHSA-26c8-35cm-xq9m
- https://github.com/nextcloud/text/pull/1884
