# [M] LF Edge eKuiper Vulnerable to Stored XSS in Configuration Key Functionality

## Summary
Severity: Medium
Advisory: GHSA-9cwv-pxcr-hfjc
CVE: CVE-2024-52290
CWE: CWE-79
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2025-05-14
Source: https://github.com/advisories/GHSA-9cwv-pxcr-hfjc
Type: github-advisory

## Affected
- Go: `github.com/lf-edge/ekuiper` — affected >=0
- Go: `github.com/lf-edge/ekuiper/v2` — affected >=0 <2.1.0

## Details
### Summary
Stored Cross-Site Scripting (XSS) vulnerability allows attackers to inject malicious scripts into web applications, which can then be executed in the context of other users' browsers. This can lead to unauthorized access to sensitive information, session hijacking, and spreading of malware, impacting user data privacy and application integrity.

### Details
A user with rights to modificate the service (e.g. kuiperUser role) can inject XSS Payload into Connection Configuration key `Name` (`confKey`) parameter. Then, after any user with access to this service (e.g. admin) will try to delete this key, a payload will act in victim's browser.

### PoC
1. Authorize as a user with rights to modificate the service (e.g. kuiperUser role).
2. Create a service or go to the existing one and access the *Configuration > Connection* page:

![*Configuration > Connection page](https://github.com/user-attachments/assets/d29cbc23-04a4-4a49-bbd9-b26f74282c5c)

3. Open any existing Connection and press on `Add configuration key`:

![image](https://github.com/user-attachments/assets/623dc76a-076c-41be-98d7-8fd42ed4e8fd)

4. Set any name and Address, then intercept the request and add the following payload to the `confKey` parameter: `123%3Cimg%20src=1%20onerror%3dalert%281%29%3E`:

![image](https://github.com/user-attachments/assets/405000db-ace9-4bca-ac52-7dc44c54a0ae)

5. A new configuration key then will be set: 

![image](https://github.com/user-attachments/assets/43b75f1e-81ac-4815-9250-c1a0707827d3)

6. *(Optional)* You can authorize another user with access to this service. For nexe steps I will use admin user
7. After we push on delete button (trash icon) opposite the created connection, the payload will work:

![image](https://github.com/user-attachments/assets/05a38899-343b-4f76-b6c7-8e27587e3cdf)


### Impact
Stored Cross-site Scripting (XSS) vulnerability

Reported by Alexey Kosmachev, Lead Pentester from Bi.Zone

## References
- https://github.com/lf-edge/ekuiper/security/advisories/GHSA-9cwv-pxcr-hfjc
- https://nvd.nist.gov/vuln/detail/CVE-2024-52290
- https://github.com/lf-edge/ekuiper/commit/943c02e10f0f8349e609474810eab5fa460d1a51
- https://github.com/lf-edge/ekuiper
