# [H] Bolt CMS vulnerable to authenticated remote code execution

## Summary
Severity: High
Advisory: GHSA-p9qc-8jjx-g8cg
CVE: CVE-2025-34086
CWE: CWE-94
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:P/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-07-03
Source: https://github.com/advisories/GHSA-p9qc-8jjx-g8cg
Type: github-advisory

## Affected
- Packagist: `bolt/bolt` — affected >=0

## Details
Bolt CMS versions 3.7.0 and earlier contain a chain of vulnerabilities that together allow an authenticated user to achieve remote code execution. A user with valid credentials can inject arbitrary PHP code into the displayname field of the user profile, which is rendered unsanitized in backend templates. The attacker can then list and rename cached session files via the /async/browse/cache/.sessions and /async/folder/rename endpoints. By renaming a .session file to a path under the publicly accessible /files/ directory with a .php extension, the attacker can turn the injected code into an executable web shell. Finally, the attacker triggers the payload via a crafted HTTP GET request to the rogue file.

NOTE: The vendor announced that Bolt 3 reached end-of-life after 31 December 2021.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-34086
- https://boltcms.io/newsitem/major-announcements-bolt-3-eol-bolt-4-2-5-0-releases
- https://github.com/bolt/bolt
- https://github.com/bolt/bolt/blob/3.7/src/Controller/Backend/Users.php#L279-L311
- https://github.com/bolt/bolt/releases/tag/3.7.1
- https://raw.githubusercontent.com/rapid7/metasploit-framework/master/modules/exploits/unix/webapp/bolt_authenticated_rce.rb
- https://www.exploit-db.com/exploits/48296
- https://www.rapid7.com/db/modules/exploit/unix/webapp/bolt_authenticated_rce
