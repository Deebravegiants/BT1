# [M] CVE-2021-34807

## Summary
Severity: Medium
Advisory: CVE-2021-34807
CVSS: 6.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N)
Published: 2021-07-02
Source: https://osv.dev/vulnerability/CVE-2021-34807
Type: osv

## Details
An open redirect vulnerability exists in the /preauth Servlet in Zimbra Collaboration Suite through 9.0. To exploit the vulnerability, an attacker would need to have obtained a valid zimbra auth token or a valid preauth token. Once the token is obtained, an attacker could redirect a user to any URL via isredirect=1&redirectURL= in conjunction with the token data (e.g., a valid authtoken= value).

## References
- https://wiki.zimbra.com/wiki/Security_Center
- https://wiki.zimbra.com/wiki/Zimbra_Releases/8.8.15/P23
- https://wiki.zimbra.com/wiki/Zimbra_Releases/9.0.0/P16
- https://wiki.zimbra.com/wiki/Zimbra_Security_Advisories
