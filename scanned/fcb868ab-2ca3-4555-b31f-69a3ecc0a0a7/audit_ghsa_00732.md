# [M] Potential unauthorized access to stored request & session data when plugin is misconfigured in October CMS Debugbar

## Summary
Severity: Medium
Advisory: GHSA-c8wh-6jw4-2h79
CVE: CVE-2020-11094
CWE: CWE-532
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2020-06-03
Source: https://github.com/advisories/GHSA-c8wh-6jw4-2h79
Type: github-advisory

## Affected
- Packagist: `rainlab/debugbar-plugin` — affected >=0 <3.1.0

## Details
### Impact
The debugbar contains a perhaps little known feature where it will log all requests (and all information pertaining to each request including session data) whenever it is enabled. This presents a problem if the plugin is ever enabled on a system that is open to untrusted users as the potential exists for them to use this feature to view all requests being made to the application and obtain sensitive information from those requests. There even exists the potential for account takeovers of authenticated users by non-authenticated public users, which would then lead to a number of other potential issues as an attacker could theoretically get full access to the system if the required conditions existed.

### Patches
Issue has been patched in v3.1.0 by locking down access to the debugbar to all users; it now requires an authenticated backend user with a specifically enabled permission before it is even usable, and the feature that allows access to stored request information is restricted behind a different permission that's more restrictive.

### Workarounds
Apply https://github.com/rainlab/debugbar-plugin/commit/86dd29f9866d712de7d98f5f9dc67751b82ecd18 to your installation manually if unable to upgrade to v3.1.0.

### For more information
If you have any questions or comments about this advisory:
* Email us at [octobercms@luketowers.ca](mailto:octobercms@luketowers.ca) & [hello@octobercms.com](mailto:hello@octobercms.com)

### Acknowledgements

Thanks to [Freddie Poser](https://twitter.com/vogonjeltz101) for reporting the issue to the RainLab team.

## References
- https://github.com/rainlab/debugbar-plugin/security/advisories/GHSA-c8wh-6jw4-2h79
- https://nvd.nist.gov/vuln/detail/CVE-2020-11094
- https://github.com/rainlab/debugbar-plugin/commit/86dd29f9866d712de7d98f5f9dc67751b82ecd18
