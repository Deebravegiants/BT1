# [M] Insecure file access in FreshRSS

## Summary
Severity: Medium
Advisory: CVE-2022-23497
Aliases: GHSA-hvrj-5fwj-p7v6
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:L)
Published: 2022-12-09
Source: https://osv.dev/vulnerability/CVE-2022-23497
Type: osv

## Details
FreshRSS is a free, self-hostable RSS aggregator. User configuration files can be accessed by a remote user. In addition to user preferences, such configurations contain hashed passwords (brypt with cost 9, salted) of FreshRSS Web interface. If the API is used, the configuration might contain a hashed password (brypt with cost 9, salted) of the GReader API, and a hashed password (MD5 salted) of the Fever API. Users should update to version 1.20.2 or edge. Users unable to upgrade can apply the patch manually or delete the file `./FreshRSS/p/ext.php`.

## References
- https://github.com/FreshRSS/FreshRSS/releases/tag/1.20.2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/23xxx/CVE-2022-23497.json
- https://github.com/FreshRSS/FreshRSS/security/advisories/GHSA-hvrj-5fwj-p7v6
- https://nvd.nist.gov/vuln/detail/CVE-2022-23497
- https://github.com/FreshRSS/FreshRSS/pull/4928
