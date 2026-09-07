# [H] WWBN/AVideo stored XSS vulnerability leads to takeover of any user's account, including admin's account

## Summary
Severity: High
Advisory: GHSA-xr9h-p2rc-rpqm
CVE: CVE-2023-30860
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-05-01
Source: https://github.com/advisories/GHSA-xr9h-p2rc-rpqm
Type: github-advisory

## Affected
- Packagist: `wwbn/avideo` — affected >=0 <12.4

## Details
In AVideo, a normal user can make a Meeting Schedule where the user can invite another user in that Meeting, but I found out that it did not properly sanitize the malicious characters when creating a Meeting Room. This leads the attacker to put malicious scripts.

Impact:

Since any USER including the ADMIN can see the meeting room that was created by the attacker this can lead to cookie hijacking and takeover of any accounts without user interaction.

Step to Reproduce:

1. As normal USER go to Meet -> Schedule

https://demo.avideo.com/plugin/Meet/

2. In "Meet topic" field put XSS payload

Example: "><img src=x onerror=alert('Pawned+by+Gonz')>

3. Then click Save

4. Now as ADMIN go to Meet -> Schedule -> Upcoming

https://demo.avideo.com/plugin/Meet/

5. Then the XSS payload that normal USER created will be executed



Video POC: https://youtu.be/Nke0Bmv5F-o

## References
- https://github.com/WWBN/AVideo/security/advisories/GHSA-xr9h-p2rc-rpqm
- https://nvd.nist.gov/vuln/detail/CVE-2023-30860
- https://github.com/WWBN/AVideo
- https://youtu.be/Nke0Bmv5F-o
