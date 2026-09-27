# [M] Missing rate limit in Authentication in bookwyrm

## Summary
Severity: Medium
Advisory: CVE-2022-35925
Aliases: GHSA-jvp3-mqv8-5rjw
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2022-08-02
Source: https://osv.dev/vulnerability/CVE-2022-35925
Type: osv

## Details
BookWyrm is a social network for tracking reading. Versions prior to 0.4.5 were found to lack rate limiting on authentication views which allows brute-force attacks. This issue has been patched in version 0.4.5. Admins with existing instances will need to update their `nginx.conf` file that was created when the instance was set up. Users are advised advised to upgrade. Users unable to upgrade may update their nginx.conf files with the changes manually.

## References
- https://huntr.dev/bounties/ebee593d-3fd0-4985-bf5e-7e7927e08bf6/
- https://www.github.com/bookwyrm-social/bookwyrm/commit/7bbe42fb30a79a26115524d18b697d895563c92f
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/35xxx/CVE-2022-35925.json
- https://github.com/bookwyrm-social/bookwyrm/security/advisories/GHSA-jvp3-mqv8-5rjw
- https://nvd.nist.gov/vuln/detail/CVE-2022-35925
