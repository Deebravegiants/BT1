# [H] MobSF Local Privilege Escalation

## Summary
Severity: High
Advisory: GHSA-79f6-p65j-3m2m
CVE: CVE-2025-24805
CWE: CWE-269
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2025-02-05
Source: https://github.com/advisories/GHSA-79f6-p65j-3m2m
Type: github-advisory

## Affected
- PyPI: `mobsf` — affected >=0 <4.3.1

## Details
**Product:** Mobile Security Framework (MobSF)
**Version:** 4.3.0
**CWE-ID:** CWE-269: Improper Privilege Management
**CVSS vector v.4.0:** 7.1 (AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:L/SI:N/SA:N)
**CVSS vector v.3.1:** 6.5 (AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
**Description:** MobSF has a functionality of dividing users by roles. This functionality is not efficient, because any registered user can get API Token with all privileges.
**Impact:** Information Disclosure 
**Vulnerable component:** Code output component (`/source_code`)
**Exploitation conditions:** authorized user
**Mitigation:** Remove token output in the returned js-script
**Researcher:** Egor Filatov (Positive Technologies)

## Research 

Researcher discovered zero-day vulnerability «Local Privilege Escalation» in Mobile Security Framework (MobSF).
To reproduce the vulnerability follow the steps below.

•	 A user with minimal privileges is required, so the administrator must create a user account

<img width="215" alt="fig1" src="https://github.com/user-attachments/assets/43e02a50-bdd9-48d9-9194-73946fcc56d9" />

*Figure 1. Registration*

•	Go to static analysis of any application

<img width="1207" alt="fig2" src="https://github.com/user-attachments/assets/9ed141a7-a667-4a96-81fd-d81127874104" />
 
*Figure 2. Static analysis*

•	Go to the code review of the selected application and get a token with all privileges in the response

<img width="1400" alt="fig3" src="https://github.com/user-attachments/assets/bf8b704b-9067-4861-a7d3-05ec119d9a3f" />
 
*Figure 3. Token receiving*

•	This token can be used to retrieve dynamic analysis information that has not been accessed before.

![fig4](https://github.com/user-attachments/assets/fda8436b-de67-45b1-bb21-6cfbc9976f79)
 
*Figure 4. No access demonstration*

<img width="1412" alt="fig5" src="https://github.com/user-attachments/assets/dc8f639f-36b0-47d3-807d-58ae551fcbfc" />
 
*Figure 5. Token usage*

As a result, the user is able to escalate the privileges.


_______________________

### Please, assign all credits to: Egor Filatov (Positive Technologies)

## References
- https://github.com/MobSF/Mobile-Security-Framework-MobSF/security/advisories/GHSA-79f6-p65j-3m2m
- https://nvd.nist.gov/vuln/detail/CVE-2025-24805
- https://github.com/MobSF/Mobile-Security-Framework-MobSF/commit/05206e72cae35b311615a70e51e1a946955c5e83
- https://github.com/MobSF/Mobile-Security-Framework-MobSF
