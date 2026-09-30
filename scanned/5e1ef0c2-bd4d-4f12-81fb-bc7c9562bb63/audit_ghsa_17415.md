# [M] Grav Exposes Password Hashes Leading to privilege escalation

## Summary
Severity: Medium
Advisory: GHSA-gq3g-666w-7h85
CVE: CVE-2025-66304
CWE: CWE-200, CWE-201
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:H/UI:N/S:U/C:H/I:H/A:L (CVSS_V3)
Published: 2025-12-02
Source: https://github.com/advisories/GHSA-gq3g-666w-7h85
Type: github-advisory

## Affected
- Packagist: `getgrav/grav` — affected >=0 <1.8.0-beta.27

## Details
# Exposure of Password Hashes Leading to privilege escalation
**Severity Rating:** Medium 

**Vector:** Privilege Escalation

**CVE:** XXX

**CWE:** 200 - Exposure of Sensitive Information

**CVSS Score:** 6.2

**CVSS Vector:** CVSS:3.1/AV:N/AC:H/PR:H/UI:N/S:U/C:H/I:H/A:L

## Analysis

It was observed that if a users is given read access on the user account management section of the admin panel can view the password hashes of all users, including the admin user. This exposure can potentially lead to privilege escalation if an attacker can crack these password hashes.

An attacker with read access can: 
* View and potentially crack the password hashes.
* Gain administrative access by cracking the admin password hash.
* Escalate privileges and compromise the entire admin panel.


## Proof of Concept

1) Give read access to user accounts to a random user as shown in the following figures:
  ![grav0](https://github.com/user-attachments/assets/020a4b47-e577-49cb-8392-bfb61491199d)
  ![grav2](https://github.com/user-attachments/assets/97fbfc46-c541-4559-9541-2b9b5de86c0e)
  

2) Log in to the admin panel with an account that has read access to user accounts and navigate to the user account management section.

3) Go to the admin profile `http://127.0.0.1/admin/accounts/users/admin`; The password is not display. Try inspecting the page source code as shown in the following figures:
  ![grav2-1](https://github.com/user-attachments/assets/057c9c14-f928-4584-99ae-4939f63dda57)
  
   You can see that it match the hash that is in the admin.yaml file :
  ![Compare to the hash in database of the admin](grav2-2.png)
  

4) Crack the hash as shown in the following figure, the algorithm use here is bcrypt:
  
![grav3](https://github.com/user-attachments/assets/ec334f80-4b87-4010-a834-cb92704a596e)
  

## Workarounds
No workaround is currently known

# Timeline
**2024-07-24** Issue identified

**2024-09-27** Vendor contacted


# About X41 D-Sec GmbH
X41 is an expert provider for application security services.
Having extensive industry experience and expertise in the area of information
security, a strong core security team of world class security experts enables
X41 to perform premium security services.

Fields of expertise in the area of application security are security centered
code reviews, binary reverse engineering and vulnerability discovery.
Custom research and IT security consulting and support services are core
competencies of X41.

## References
- https://github.com/getgrav/grav/security/advisories/GHSA-gq3g-666w-7h85
- https://nvd.nist.gov/vuln/detail/CVE-2025-66304
- https://github.com/getgrav/grav/commit/9d11094e4133f059688fad1e00dbe96fb6e3ead7
- https://github.com/getgrav/grav
