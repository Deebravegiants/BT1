# [H] Firebird Non-Authorized Access to Encrypted Database Using Execute Statement on External

## Summary
Severity: High
Advisory: CVE-2025-24975
Aliases: GHSA-fx9r-rj68-7p69
CVSS: 7.1 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:L)
Published: 2025-08-15
Source: https://osv.dev/vulnerability/CVE-2025-24975
Type: osv

## Details
Firebird is a relational database. Prior to snapshot versions 4.0.6.3183, 5.0.2.1610, and 6.0.0.609, Firebird is vulnerable if ExtConnPoolSize is not set equal to 0. If connections stored in ExtConnPool are not verified for presence and suitability of the CryptCallback interface is used when created versus what is available could result in a segfault in the server process. Encrypted databases, accessed by execute statement on external, may be accessed later by an attachment missing a key to that database. In a case when execute statement are chained, segfault may happen. Additionally, the segfault may affect unencrypted databases. This issue has been patched in snapshot versions 4.0.6.3183, 5.0.2.1610, and 6.0.0.609 and point releases 4.0.6 and 5.0.2. A workaround for this issue involves setting ExtConnPoolSize equal to 0 in firebird.conf.

## References
- https://www.vicarius.io/vsociety/posts/cve-2025-24975-detect-vulnerable-firebird
- https://www.vicarius.io/vsociety/posts/cve-2025-24975-mitigate-firebird-vulnerability
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/24xxx/CVE-2025-24975.json
- https://github.com/FirebirdSQL/firebird/security/advisories/GHSA-fx9r-rj68-7p69
- https://nvd.nist.gov/vuln/detail/CVE-2025-24975
- https://github.com/FirebirdSQL/firebird/issues/8429
- https://github.com/FirebirdSQL/firebird/commit/658abd20449f72097fbbce57e8e6ae42ff837fb6
