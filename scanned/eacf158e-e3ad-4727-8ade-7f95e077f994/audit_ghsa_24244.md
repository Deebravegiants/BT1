# [M] Use of a Broken or Risky Cryptographic Algorithm in XWiki Crypto API

## Summary
Severity: Medium
Advisory: GHSA-h8v5-p258-pqf4
CVE: CVE-2022-29161
CWE: CWE-326, CWE-327
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-h8v5-p258-pqf4
Type: github-advisory

## Affected
- Maven: `org.xwiki.platform:xwiki-platform-crypto` — affected >=0 <13.10.6
- Maven: `org.xwiki.platform:xwiki-platform-crypto` — affected >=14.0.0 <14.3.1

## Details
### Impact
XWiki Crypto API will generate X509 certificates signed by default using SHA1 with RSA, which is not considered safe anymore for use in certificate signatures, due to the risk of collisions with SHA1.
Note that this API is never used in XWiki Standard but it might be used in some extensions of XWiki.

### Patches
The problem has been patched in XWiki version 13.10.6, 14.3.1 and 14.4-rc-1. Since then, the Crypto API will generate X509 certificates signed by default using SHA256 with RSA.

### Workarounds
Administrators are advised to upgrade their XWiki installation to one of the patched versions.
If the upgrade is not possible, it is possible to patch the module xwiki-platform-crypto in a local installation by applying the change exposed in https://github.com/xwiki/xwiki-platform/commit/26728f3f23658288683667a5182a916c7ecefc52 and re-compiling the module.

### References
https://jira.xwiki.org/browse/XWIKI-19676
https://github.com/openssl/openssl/blob/master/CHANGES.md?plain=1#L938
https://github.com/openssl/openssl/issues/16650

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [Jira XWiki](https://jira.xwiki.org)
* Email us at [security ML](mailto:security@xwiki.org)

## References
- https://github.com/xwiki/xwiki-platform/security/advisories/GHSA-h8v5-p258-pqf4
- https://nvd.nist.gov/vuln/detail/CVE-2022-29161
- https://github.com/xwiki/xwiki-platform/commit/26728f3f23658288683667a5182a916c7ecefc52
- https://github.com/xwiki/xwiki-platform
- https://jira.xwiki.org/browse/XWIKI-19676
