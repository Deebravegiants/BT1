# [H] DoS vulnerabilities persist in ESAPI file uploads despite remediation of CVE-2023-24998

## Summary
Severity: High
Advisory: GHSA-7c2q-5qmr-v76q
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-10-27
Source: https://github.com/advisories/GHSA-7c2q-5qmr-v76q
Type: github-advisory

## Affected
- Maven: `org.owasp.esapi:esapi` — affected >=0 <2.5.2.0

## Details
### Impact
ESAPI 2.5.2.0 and later addressed  the DoS vulnerability described in CVE-2023-24998, which Apache Commons FileUpload 1.5 attempted to remediate. But while writing up a new security bulletin regarding the impact on the affected ESAPI `HTTPUtilities.getFileUploads` methods (or more specifically those methods in the `DefaultHTTPUtilities` implementation class), I realized that a DoS vulnerability still persists in ESAPI and for that matter in Apache Commons FileUpload as well.

### Related to
CVE-2023-24998

### Patches
ESAPI 2.5.2.0 or later.

### Workarounds
- See the 'Solutions' section of Security Bulletin 11, in the References section. If you are not using ESAPI file uploads, see also the 'Workarounds' section.
- Deploy an external WAF or other suitable DoS protection.
- Add additional defenses to your code using HTTPUtilities.getFileUpload, such as requiring prior authentication, restricting how many / much content can be uploaded per user per day or per hour, etc. (It is the opinion of the ESAPI development team that such required controls should not be added to ESAPI because it is a general purpose security library and thus ESAPI ought not be enforcing generic policies like these on everyone, especially it it could break existing code bases.)

### References
[Security Bulletin 11: How Does CVE-2023-24998 Impact ESAPI?](https://github.com/ESAPI/esapi-java-legacy/blob/develop/documentation/ESAPI-security-bulletin11.pdf)
New ESAPI 2.5.2.0  or later Javadoc on HTTPUtilities.getFileUploads: https://javadoc.io/static/org.owasp.esapi/esapi/2.5.2.0/org/owasp/esapi/HTTPUtilities.html#getFileUploads-javax.servlet.http.HttpServletRequest-java.io.File-java.util.List-
(Note: This link won't work until the 2.5.2.0 release is made official.)

### Final Word
(Especially to GitHub Advance Security team / GitHub as a CNA) -- I do not really wish to file a CVE for this. I had originally considered it, but there is no real way to address the general DoS scenarios for file uploads without breaking ESAPI client code which we are not willing to do. The clients have to take some responsibility for this themselves. In the next ESAPI release, I am going to add a reference to the appropriate Javadoc to this GitHub Security Advisory, but that's the best we can do. If you wish to discuss this with me, please first contact me via email at kevin.w.wall@gmail.com.

## References
- https://github.com/ESAPI/esapi-java-legacy/security/advisories/GHSA-7c2q-5qmr-v76q
- https://github.com/ESAPI/esapi-java-legacy
