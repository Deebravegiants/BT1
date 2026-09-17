# [H] Froxlor username/surname AND company field Bypass

## Summary
Severity: High
Advisory: GHSA-625g-fm5w-w7w4
CVE: CVE-2023-50256
CWE: CWE-20
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2024-01-04
Source: https://github.com/advisories/GHSA-625g-fm5w-w7w4
Type: github-advisory

## Affected
- Packagist: `froxlor/froxlor` — affected >=0 <2.1.2

## Details
Dear Sirs and Madams,

I would like to report a business logic error vulnerability that I discovered during my recent penetration test on Froxlor.

Specifically, I identified an issue where it was possible to submit the registration form with the essential fields, such as the username and password, left intentionally blank. This inadvertent omission allowed for a bypass of the mandatory field requirements established by the system.

The surname, family name AND company name all of them can be left blank.

I believe addressing this vulnerability is crucial to ensure the security and integrity of the Froxlor platform.

Thank you for your attention to this matter.

This action served as a means to bypass the mandatory field requirements.

Lets see (please have a look at the Video -> attachment).

----------------

as you can see i was able to let the username and second name blank. 

https://user-images.githubusercontent.com/80028768/289675319-81ae8ebe-1308-4ee3-bedb-43cdc40da474.mp4


Lets see again.

Only the company name is set. 

Thank you for your time

![Froxlor 2](https://user-images.githubusercontent.com/80028768/289685700-73936e19-befa-4442-a258-7814f2ec4598.png)
![Froxlor 1](https://user-images.githubusercontent.com/80028768/289685710-a5785f49-d2b2-40d4-bf8f-a286df48dd36.png)

## References
- https://github.com/Froxlor/Froxlor/security/advisories/GHSA-625g-fm5w-w7w4
- https://nvd.nist.gov/vuln/detail/CVE-2023-50256
- https://github.com/Froxlor/Froxlor/commit/4b1846883d4828962add91bd844596d89a9c7cac
- https://github.com/Froxlor/Froxlor
- https://user-images.githubusercontent.com/80028768/289675319-81ae8ebe-1308-4ee3-bedb-43cdc40da474.mp4
