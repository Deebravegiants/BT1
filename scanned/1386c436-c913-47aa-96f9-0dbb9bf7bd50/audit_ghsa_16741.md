# [C] Blind XSS Leading to Froxlor Application Compromise

## Summary
Severity: Critical
Advisory: GHSA-x525-54hf-xr53
CVE: CVE-2024-34070
CWE: CWE-79, CWE-80
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2024-05-10
Source: https://github.com/advisories/GHSA-x525-54hf-xr53
Type: github-advisory

## Affected
- Packagist: `froxlor/froxlor` — affected >=0 <2.1.9

## Details
### Description:

A Stored Blind Cross-Site Scripting (XSS) vulnerability has been identified in the Failed Login Attempts Logging Feature of the Froxlor Application. Stored Blind XSS occurs when user input is not properly sanitized and is stored on the server, allowing an attacker to inject malicious scripts that will be executed when other users access the affected page. In this case, an unauthenticated User can inject malicious scripts in the loginname parameter on the Login attempt, which will then be executed when viewed by the Administrator in the System Logs.

The application protects users against XSS attacks by utilizing an xss sanitization library. But the checks of the library were bypassed by crafting an XSS Payload using data binding and interpolation of Vue.js

A working XSS payload was crafted which forces an administrator to add a new malicious attacker-controlled Administrator User. The Payload is:
[payload.txt](https://github.com/froxlor/Froxlor/files/15142616/payload.txt)


By exploiting this vulnerability, an unauthenticated attacker can force the Administrator to perform actions without the administrator even noticing anything suspicious. In one scenario, I made an exploit that forced the administrator to add an attacker-controlled Administrator into the Froxlor Application, resulting in a compromise of the Froxlor Application.

### Impact:
The impact of this vulnerability is severe as it allows an attacker to compromise the Froxlor Application. By exploiting this vulnerability, the attacker can perform various malicious actions such as forcing the Administrator to execute actions without their knowledge or consent. For instance, the attacker can force the Administrator to add a new administrator controlled by the attacker, thereby giving the attacker full control over the application.

Attackers can steal sensitive information such as login credentials, session tokens, and personally identifiable information (PII).

The vulnerability can lead to defacement of the Application.


### Mitigation:
Implement thorough input validation and sanitization mechanisms on all user inputs. This will help prevent malicious scripts from being stored and executed. sanitize {{ and }} to prevent data binding and interpolation of Vue.js.
Sanitize malicious Javascript functions. Etc.

### Steps to Reproduce:

**Attacker Steps:**
1. Provide an invalid username in Login.
2. Turn on intercept in Burp Suite.
3. In the intercepted request, add the following XSS payload as the value of loginname parameter (Copy from below file):
[payload.txt](https://github.com/froxlor/Froxlor/files/15142616/payload.txt)
4. Turn off the intercept.

**Victim Steps:**
5. Login as admin.
6. Go to System Logs, XSS payload will be executed and a popup will appear showing that the Application has been compromised.

**Attacker Step:**
7. Back at the Attacker's side, log in to the newly created attacker-controlled admin account having all the privileges. The credentials will be username: `abcd` & Password: `abcd@@1234`

### Evidence:

![image](https://github.com/froxlor/Froxlor/assets/59286712/31cf0cb8-b0e4-46d0-a6b8-a0e22fda64b8)
_Figure 1: Code of Logging Invalid login attempts_

![image](https://github.com/froxlor/Froxlor/assets/59286712/6acef52a-d5ba-477d-b502-a7fe27fd5085)
_Figure 2: Code of saving Logs._

![image](https://github.com/froxlor/Froxlor/assets/59286712/2adf8ae5-66be-4e22-938b-c9e5dcb764c0)
_Figure 3: Attacker injecting XSS payload._

![image](https://github.com/froxlor/Froxlor/assets/59286712/d3ccf6f9-2a23-40a4-97fc-e9585553ac52)
_Figure 4: XSS payload Executed._

![image](https://github.com/froxlor/Froxlor/assets/59286712/3c7f24f6-4049-49d3-978b-d83800fe8a80)
_Figure 5: XSS payload Reflection._

### Video POC

https://github.com/froxlor/Froxlor/assets/59286712/7ba7d3e7-9ee9-4e64-988c-33fd4ebbca27

## References
- https://github.com/froxlor/Froxlor/security/advisories/GHSA-x525-54hf-xr53
- https://nvd.nist.gov/vuln/detail/CVE-2024-34070
- https://github.com/froxlor/Froxlor/commit/a862307bce5cdfb1c208b835f3e8faddd23046e6
- https://github.com/froxlor/Froxlor
