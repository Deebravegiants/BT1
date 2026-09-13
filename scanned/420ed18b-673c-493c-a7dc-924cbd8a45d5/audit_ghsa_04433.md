# [C] motionEye: Authentication possible via password hash

## Summary
Severity: Critical
Advisory: GHSA-r3cw-c95m-wfh9
CVE: CVE-2026-46488
CWE: CWE-256, CWE-287, CWE-328, CWE-836
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-06-22
Source: https://github.com/advisories/GHSA-r3cw-c95m-wfh9
Type: github-advisory

## Affected
- PyPI: `motioneye` — affected >=0 <0.44.0

## Details
### Summary
An authentication bypass vulnerability exists due to improper trust in client-controlled cookies. The application accepts user-supplied cookie values containing a username and password-hash-derived value as sufficient authentication material. These cookies can be set or modified prior to login, allowing an unauthenticated attacker to impersonate arbitrary users without knowledge of the plaintext password. This issue stems from the absence of server-side validation of authentication state and reliance on attacker-controlled cookie data

### Details
The vulnerability arises because the application accepts the client-supplied cookies named `meye_password_hash` and `meye_username` as sufficient authentication material. The server does not validate these values against a server-side session or enforce proper authentication checks before establishing an authenticated state. As a result, an unauthenticated attacker can set or modify these cookies to impersonate another user if the target username and corresponding hash are known.

These cookies normally appear after using the "switch user" functionality; however, they can be added manually prior to authentication using standard browser tools (e.g., developer tools or cookie editors) or dynamically loaded by submitting blank credentials. When supplied, the server accepts them and authenticates the attacker as the specified user bypassing the intended authentication flow

Additionally, the password-hash value and username for the admin account used by the application is stored in `/etc/motioneye/motion.conf` which is globally readable by default on the local system. This means any local user with shell access can obtain a valid hash and values and use them to impersonate the admin via the cookie manipulation described above. While local access is required to retrieve the hash, this significantly lowers the barrier to exploitation in multi-user environments. 

### PoC
Starting state unauthenticated with no cookies:
<img width="644" height="475" alt="start state" src="https://github.com/user-attachments/assets/cf4aff78-65f7-4f67-99e2-9134c8f04277" />

After manually adding or submitting blank credentials to get the cookies loaded:
<img width="643" height="470" alt="empty cookies" src="https://github.com/user-attachments/assets/223878eb-f085-4ac5-a92a-2ac21831c594" />


Adding the credentials and refreshing the page gives us a valid session:
<img width="641" height="466" alt="admin login with hash" src="https://github.com/user-attachments/assets/94b350ef-dd32-4cae-8bd8-e48841873f79" />


version information and session interaction validation
<img width="643" height="468" alt="verison" src="https://github.com/user-attachments/assets/94290ad6-4e82-4026-8e27-5374e2f3a631" />


### Impact
Authentication bypass

### Who is impacted?

Any MotionEye deployment where attackers have access to a username and hash, and/or the `/etc/motioneye/motion.conf` file with the admin username and hash.

Potential consequences:

- Account lockouts 
- Attacker persistence by changing the password
- Enumeration of data
- Destruction of data
- Exfiltration of data

## References
- https://github.com/motioneye-project/motioneye/security/advisories/GHSA-r3cw-c95m-wfh9
- https://github.com/motioneye-project/motioneye
