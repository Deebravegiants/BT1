# [H] botframework-connector vulnerable to Improper Authentication

## Summary
Severity: High
Advisory: GHSA-cqff-fx2x-p86v
CWE: CWE-287
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2021-03-08
Source: https://github.com/advisories/GHSA-cqff-fx2x-p86v
Type: github-advisory

## Affected
- PyPI: `botframework-connector` — affected >=4.7.0 <4.7.2
- PyPI: `botframework-connector` — affected >=4.8.0 <4.8.1
- PyPI: `botframework-connector` — affected >=4.9.0 <4.9.3
- PyPI: `botframework-connector` — affected >=4.10.0 <4.10.1

## Details
### Impact
A maliciously crafted claim may be incorrectly authenticated by the bot. Impacts bots that are not configured to be used as a Skill. This vulnerability requires an attacker to have internal knowledge of the bot.

### Patches
The problem has been patched in all affected versions. Please see the list of patched versions for the most appropiate one for your individual case.

### Workarounds
Users who do not wish or are not able to upgrade can add an authentication configuration containing ClaimsValidator, which throws an exception if Claims are Skill Claims. 

For detailed instructions, see the link in the References section.

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [Microsoft Bot Builder SDK](https://github.com/microsoft/botframework-sdk)
* Email us at [bf-reports@microsoft.com](mailto:bf-reports@microsoft.com)

## References
- https://github.com/microsoft/botbuilder-python/security/advisories/GHSA-cqff-fx2x-p86v
- https://github.com/microsoft/botbuilder-python/blob/main/doc/SkillClaimsValidation.md
- https://github.com/pypa/advisory-database/tree/main/vulns/botframework-connector/PYSEC-2021-422.yaml
- https://portal.msrc.microsoft.com/en-US/security-guidance/advisory/CVE-2021-1725
- https://pypi.org/project/botframework-connector
