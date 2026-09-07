# [M] Leantime allows Stored Cross-Site Scripting (XSS)

## Summary
Severity: Medium
Advisory: GHSA-63cr-xg3f-8jvr
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:P/VC:L/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-02-21
Source: https://github.com/advisories/GHSA-63cr-xg3f-8jvr
Type: github-advisory

## Affected
- Packagist: `leantime/leantime` — affected >=0

## Details
### Summary
Stored XSS, also known as persistent XSS, is the more damaging of the two. It occurs when a malicious script is injected directly into a vulnerable web application. 

### Details
A Stored Cross-Site Scripting (XSS) vulnerability was found that could potentially compromise user data and pose a significant security risk to the platform.

### PoC

- Create a project
- Navigate to project
- Visit to the integration
- Add malicious payload inside the webhook and save it.
- Notice the alert dialogue indicating successful execution of the XSS payload.
```
'';!--" onfocus=alert(0) autofocus=""  onload=alert(3);="&amp;{(alert(1))}" |="" mufazmi"="
```
```
'';!--" onfocus=alert(0) autofocus=""  onload=alert(3);=>>"&amp;{(alert(1))}" |="">> mufazmi"=">>
```
### POC
https://youtu.be/kqKFgsOqstg


### Impact
This XSS vulnerability allows an attacker to execute malicious scripts in the context of a victim's browser when they click on a specially crafted link. This could lead to various malicious activities, including session hijacking, stealing sensitive information such as cookies or login credentials, and potentially compromising the entire platform's security.

## References
- https://github.com/Leantime/leantime/security/advisories/GHSA-63cr-xg3f-8jvr
- https://github.com/Leantime/leantime
- https://youtu.be/kqKFgsOqstg
