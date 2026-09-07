# [M] Taipy has a Session Cookie without Secure and HTTPOnly flags

## Summary
Severity: Medium
Advisory: GHSA-r3jq-4r5c-j9hp
CVE: CVE-2024-47833
CWE: CWE-1004, CWE-319, CWE-614
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2024-08-27
Source: https://github.com/advisories/GHSA-r3jq-4r5c-j9hp
Type: github-advisory

## Affected
- PyPI: `taipy` — affected >=0 <4.0.0

## Details
### Summary
Session cookie is without Secure and HTTPOnly flags.

### Details
Please take a look at this part of code (PoC screenshot) or check code directly (provided in Occurrences section below)

**Occurrences**:
https://github.com/Avaiga/taipy/blob/develop/frontend/taipy-gui/src/components/Taipy/Navigate.tsx#L67

**Proposed remediation:** add Secure and HTTPOnly flags for cookies.

It could be like this:
document.cookie = `tprh=${tprh};path=/;Secure;HttpOnly;`;


### PoC
**Screenshot**:
![image](https://github.com/Avaiga/taipy/assets/18367606/ea7d1bbd-ba27-447f-932b-3d33ffc1a2e7)


### Impact
**Secure**: This flag indicates that the cookie should only be sent over secure HTTPS connections. Without this flag, the cookie will be sent over both HTTP and HTTPS connections, which could expose it to interception or tampering if the connection is not secure.
**HttpOnly:** This flag prevents the cookie from being accessed by client-side JavaScript. It helps mitigate certain types of attacks, such as cross-site scripting (XSS), by preventing malicious scripts from accessing the cookie's value.

**References**
    CWE-614: Sensitive Cookie in HTTPS Session Without 'Secure' Attribute https://cwe.mitre.org/data/definitions/614.html
    CWE-1004: Sensitive Cookie Without 'HttpOnly' Flag - https://cwe.mitre.org/data/definitions/1004.html
    OWASP - Secure Cookie Attribute - https://owasp.org/www-community/controls/SecureCookieAttribute
    Cookie security flags - https://www.invicti.com/learn/cookie-security-flags/
    Cookie lack Secure flag - https://support.detectify.com/support/solutions/articles/48001048982-cookie-lack-secure-flag

**Other**:
Title: Encrypting the Web
URL: https://www.eff.org/encrypt-the-web

Update (Required advisory information) - added severity, resource: 
https://portswigger.net/kb/issues/00500200_tls-cookie-without-secure-flag-set

Best regards,

## References
- https://github.com/Avaiga/taipy/security/advisories/GHSA-r3jq-4r5c-j9hp
- https://nvd.nist.gov/vuln/detail/CVE-2024-47833
- https://github.com/Avaiga/taipy
- https://github.com/Avaiga/taipy/blob/develop/frontend/taipy-gui/src/components/Taipy/Navigate.tsx#L67
- https://github.com/pypa/advisory-database/tree/main/vulns/taipy/PYSEC-2024-168.yaml
