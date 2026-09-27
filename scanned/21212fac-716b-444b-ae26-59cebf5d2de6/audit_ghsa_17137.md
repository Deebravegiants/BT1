# [H] OneUptime Vulnerable to a Privilege Escalation via Local Storage Key Manipulation

## Summary
Severity: High
Advisory: GHSA-246p-xmg8-wmcq
CVE: CVE-2024-29194
CWE: CWE-639
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:L (CVSS_V3)
Published: 2024-03-25
Source: https://github.com/advisories/GHSA-246p-xmg8-wmcq
Type: github-advisory

## Affected
- npm: `@oneuptime/model` — affected >=0 <7.0.1815
- npm: `@oneuptime/common-server` — affected >=0 <7.0.1815

## Details
## Summary
A security vulnerability exists in oneuptime's local storage handling, where a regular user can escalate privileges by modifying the `is_master_admin` key to `true`. This allows unauthorized access to administrative functionalities.

## Details
The vulnerability lies in the improper validation of client-side stored data within the web application. Specifically, the `is_master_admin` key, stored in the local storage of the browser, can be manipulated by an attacker. By changing this key from false to true, the application grants administrative privileges to the user, without proper server-side validation. 

## POC
(I am using Firefox Developer to demonstrate this vulnerability)
Log in as a normal user. Open developer tools (hit F12), click Storage, then Local Storage. Modify the `is_master_admin` key from `false` to `true`.

## Impact
This vulnerability represents a high security risk as it allows any authenticated user to gain administrative privileges through client-side manipulation. Most of the admin previlages were disabled except the user list. Where an attacker could see all the list of users who signed up to OneUptome. 


## Patch
This has been patched in 7.0.1815

## References
- https://github.com/OneUptime/oneuptime/security/advisories/GHSA-246p-xmg8-wmcq
- https://nvd.nist.gov/vuln/detail/CVE-2024-29194
- https://github.com/OneUptime/oneuptime/commit/14016d23d834038dd65d3a96cf71af04b556a32c
- https://github.com/OneUptime/oneuptime
