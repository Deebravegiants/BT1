# [M] CVE-2021-32725

## Summary
Severity: Medium
Advisory: CVE-2021-32725
Aliases: GHSA-6f6v-h9x9-jj4v
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2021-07-12
Source: https://osv.dev/vulnerability/CVE-2021-32725
Type: osv

## Details
Nextcloud Server is a Nextcloud package that handles data storage. In versions prior to 19.0.13, 20.011, and 21.0.3, default share permissions were not being respected for federated reshares of files and folders. The issue was fixed in versions 19.0.13, 20.0.11, and 21.0.3. There are no known workarounds.

## References
- https://github.com/nextcloud/security-advisories/security/advisories/GHSA-6f6v-h9x9-jj4v
- https://security.gentoo.org/glsa/202208-17
- https://hackerone.com/reports/1178320
- https://github.com/nextcloud/server/pull/26946
