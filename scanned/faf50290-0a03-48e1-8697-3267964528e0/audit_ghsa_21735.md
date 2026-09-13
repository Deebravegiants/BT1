# [M] b2-sdk-python TOCTOU application key disclosure 

## Summary
Severity: Medium
Advisory: GHSA-p867-fxfr-ph2w
CVE: CVE-2022-23651
CWE: CWE-367
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-02-24
Source: https://github.com/advisories/GHSA-p867-fxfr-ph2w
Type: github-advisory

## Affected
- PyPI: `b2sdk` — affected >=0 <1.14.1

## Details
### Impact

Linux and Mac releases of the SDK version 1.14.0 and below contain a key disclosure vulnerability that, in certain conditions, can be exploited by local attackers through a time-of-check-time-of-use (TOCTOU) race condition.

SDK users of the `SqliteAccountInfo` format are vulnerable while users of the `InMemoryAccountInfo` format are safe. The `SqliteAccountInfo` saves API keys (and bucket name-to-id mapping) in a local database file (`$XDG_CONFIG_HOME/b2/account_info`, `~/.b2_account_info` or a user-defined path). When first created, the file is world readable and is (typically a few milliseconds) later altered to be private to the user. If the directory containing the file is readable by a local attacker then during the brief period between file creation and permission modification, a local attacker can race to open the file and maintain a handle to it. This allows the local attacker to read the contents after the file after the sensitive information has been saved to it.

Consumers of this SDK who rely on it to save data using `SqliteAccountInfo` class should upgrade to the latest version of the SDK. Those who believe a local user might have opened a handle using this race condition, should remove the affected database files and regenerate all application keys.

### Patches
Users should upgrade to b2-sdk-python 1.14.1 or later.

### For more information
See the related advisory in the [B2 Command Line Tool](https://github.com/Backblaze/B2_Command_Line_Tool), a consumer of this SDK.

If you have any questions or comments about this advisory:
* Open an issue in [b2-sdk-python](https://github.com/Backblaze/b2-sdk-python)
* Email us at [security@backblaze.com](mailto:security@backblaze.com)

## References
- https://github.com/Backblaze/b2-sdk-python/security/advisories/GHSA-p867-fxfr-ph2w
- https://nvd.nist.gov/vuln/detail/CVE-2022-23651
- https://github.com/Backblaze/b2-sdk-python/commit/62476638986e5b6d7459aca5ef8ce220760226e0
- https://github.com/Backblaze/b2-sdk-python
- https://github.com/pypa/advisory-database/tree/main/vulns/b2sdk/PYSEC-2022-33.yaml
- https://pypi.org/project/b2sdk
