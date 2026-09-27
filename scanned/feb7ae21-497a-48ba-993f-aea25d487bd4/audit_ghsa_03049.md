# [C] October CMS Session ID not invalidated after logout

## Summary
Severity: Critical
Advisory: GHSA-7ggw-h8pp-r95r
CVE: CVE-2021-3311
CWE: CWE-613
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-02-10
Source: https://github.com/advisories/GHSA-7ggw-h8pp-r95r
Type: github-advisory

## Affected
- Packagist: `october/rain` — affected >=0 <1.0.472
- Packagist: `october/rain` — affected >=1.1.0 <1.1.2

## Details
### Impact
When logging out, the session ID was not invalidated. This is not a problem while the user is logged out, but as soon as the user logs back in the old session ID would be valid again; which means that anyone that gained access to the old session cookie would be able to act as the logged in user. This is not a major concern for the majority of cases, since it requires a malicious party gaining access to the session cookie in the first place, but nevertheless has been fixed.

### Patches
Issue has been patched in Build 472 (v1.0.472) and v1.1.2.

### Workarounds
Apply https://github.com/octobercms/library/commit/642f597489e6f644d4bd9a0c267e864cabead024 to your installation manually if unable to upgrade to Build 472 or v1.1.2.

### References
- Reported by Anisio (Brazilian Information Security Analyst)
- http://cve.circl.lu/cve/CVE-2021-3311

### For more information
If you have any questions or comments about this advisory:
* Email us at [hello@octobercms.com](mailto:hello@octobercms.com)

### Threat assessment:
<img width="699" alt="Screen Shot 2021-02-07 at 11 50 35 PM" src="https://user-images.githubusercontent.com/7253840/107180881-51eaf000-699f-11eb-8828-333128faf2a6.png">

## References
- https://github.com/octobercms/october/security/advisories/GHSA-7ggw-h8pp-r95r
- https://nvd.nist.gov/vuln/detail/CVE-2021-3311
- https://github.com/octobercms/library/commit/642f597489e6f644d4bd9a0c267e864cabead024
- https://anisiosantos.me/october-cms-token-reactivation
- https://octobercms.com/forum/chan/announcements
- https://packagist.org/packages/october/rain
- http://cve.circl.lu/cve/CVE-2021-3311
