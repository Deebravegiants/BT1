# [M] Craft CMS: Entries Authorship Spoofing via Mass Assignment

## Summary
Severity: Medium
Advisory: GHSA-2xfc-g69j-x2mp
CVE: CVE-2026-28781
CWE: CWE-639, CWE-915
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N/E:P (CVSS_V4)
Published: 2026-03-03
Source: https://github.com/advisories/GHSA-2xfc-g69j-x2mp
Type: github-advisory

## Affected
- Packagist: `craftcms/cms` — affected >=5.0.0-RC1 <5.9.0-beta.1
- Packagist: `craftcms/cms` — affected >=4.0.0-RC1 <4.17.0-beta.1

## Details
## Description
The entry creation process allows for **Mass Assignment** of the `authorId` attribute. A user with "Create Entries" permission can inject the `authorIds[]` (or `authorId`) parameter into the POST request, which the backend processes without verifying if the current user is authorized to assign authorship to others.

Normally, this field is not present in the request for users without the necessary permissions. By manually adding this parameter, an attacker can attribute the new entry to any user, including Admins. This effectively "spoofs" the authorship.

## Proof of Concept
### Prerequisites
- A user account with "Create Entries" permission for a section.
- Victim's account ID (e.g., `1` for the default Admin).

### Steps to Reproduce
1. Log in as the attacker
1. Navigate to the "Entries" section and click "New Entry"
1. Fill in the required fields
1. Enable a proxy tool (e.g., Burp Suite) to intercept requests
1. Click "Save" & Intercept the request
1. In the request body, add a new parameter to the body params: `&authorIds[]=<Victim_ID>`
1. Forward the request
1. Log in as an admin / as with the victim account
1. Go to entries & Observe the newly created entry is listed and the author is the victim account, not the actual creator

## Impact
- A user can create entries that appear to belong to higher-privileged users, potentially bypassing review processes or gaining trust based on false authorship.
- An attacker could post malicious or inappropriate content attributed to an administrator or other trusted users.

## Resources

https://github.com/craftcms/cms/commit/c6dcbdffaf6ab3ffe77d317336684d83699f4542
https://github.com/craftcms/cms/commit/830b403870cd784b47ae42a3f5a16e7ac2d7f5a8

## References
- https://github.com/craftcms/cms/security/advisories/GHSA-2xfc-g69j-x2mp
- https://nvd.nist.gov/vuln/detail/CVE-2026-28781
- https://github.com/craftcms/cms/commit/830b403870cd784b47ae42a3f5a16e7ac2d7f5a8
- https://github.com/craftcms/cms/commit/c6dcbdffaf6ab3ffe77d317336684d83699f4542
- https://github.com/craftcms/cms
