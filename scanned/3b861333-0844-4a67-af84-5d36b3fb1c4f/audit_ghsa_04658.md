# [H] Gogs has the ability to import local repositories via Mirror Settings

## Summary
Severity: High
Advisory: GHSA-wv27-2vqp-j7g5
CVE: CVE-2026-52801
CWE: CWE-20
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H (CVSS_V3)
Published: 2026-06-23
Source: https://github.com/advisories/GHSA-wv27-2vqp-j7g5
Type: github-advisory

## Affected
- Go: `gogs.io/gogs` — affected >=0 <0.14.3

## Details
### Summary
The Gogs Mirror Settings functionality provide an alternative way from the well protected New Migration functionality for any authenticated users to import local repositories. This issue stems from a lack of validation of SaveAddress function.

### Details
Here is the function implementation of the secure New Migration functionality.
<img width="1200" height="755" alt="image" src="https://github.com/user-attachments/assets/a6c2f307-715e-4451-bbc1-7bd934d56f96" />

Here is the function implementation of the Mirror Settings without any validation.
<img width="1200" height="477" alt="image" src="https://github.com/user-attachments/assets/a11c41b8-1d08-499c-bce6-ab40844211d7" />

### PoC
The New Migration feature correctly blocked my attempt to import a local repository.
<img width="1200" height="1008" alt="image" src="https://github.com/user-attachments/assets/dfc5aa3f-1cc4-427d-b7fe-274363c83c4e" />

But if I create a normal migration with a valid repository.
<img width="1200" height="1006" alt="image" src="https://github.com/user-attachments/assets/c96b356e-8ca9-4e79-a69b-ff14593c0cac" />

Then, I could use the Mirror Settings feature under the Repository Settings sync a local repository.
<img width="1200" height="476" alt="image" src="https://github.com/user-attachments/assets/9105475c-ae68-4d93-96d5-a3ec356deba7" />

Here is the result after the sync.
<img width="1200" height="533" alt="image" src="https://github.com/user-attachments/assets/1df76642-3e55-4493-a422-f7f0619b463d" />


### Impact
Users can import local repositories from the server's filesystem, which allows accessing any repository the git user has access to. There is also a potential issue of blind SSRF.

## References
- https://github.com/gogs/gogs/security/advisories/GHSA-wv27-2vqp-j7g5
- https://nvd.nist.gov/vuln/detail/CVE-2026-52801
- https://github.com/gogs/gogs/pull/8225
- https://github.com/gogs/gogs/commit/11e19f28b5c82466fd1689c94344ef4313ee986c
- https://github.com/gogs/gogs
- https://github.com/gogs/gogs/releases/tag/v0.14.3
