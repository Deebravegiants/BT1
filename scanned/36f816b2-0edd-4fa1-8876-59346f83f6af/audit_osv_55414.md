# [M] CVE-2025-43926

## Summary
Severity: Medium
Advisory: CVE-2025-43926
CVSS: 6.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N)
Published: 2025-05-08
Source: https://osv.dev/vulnerability/CVE-2025-43926
Type: osv

## Details
An issue was discovered in Znuny through 6.5.14 and 7.x through 7.1.6. Custom AJAX calls to the AgentPreferences UpdateAJAX subaction can be used to set user preferences with arbitrary keys. When fetching user data via GetUserData, these keys and values are retrieved and given as a whole to other function calls, which then might use these keys/values to affect permissions or other settings.

## References
- https://znuny.com
- https://www.znuny.org/en/advisories/zsa-2025-07
