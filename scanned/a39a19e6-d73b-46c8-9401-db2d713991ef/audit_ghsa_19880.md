# [M] LF Edge eKuiper allows Stored XSS in Rules Functionality

## Summary
Severity: Medium
Advisory: GHSA-6hrw-x7pr-4mp8
CVE: CVE-2024-52812
CWE: CWE-79
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2025-03-10
Source: https://github.com/advisories/GHSA-6hrw-x7pr-4mp8
Type: github-advisory

## Affected
- Go: `github.com/lf-edge/ekuiper/v2` — affected >=0 <2.0.8
- Go: `github.com/lf-edge/ekuiper` — affected >=0

## Details
### Summary
Stored Cross-Site Scripting (XSS) vulnerability allows attackers to inject malicious scripts into web applications, which can then be executed in the context of other users' browsers. This can lead to unauthorized access to sensitive information, session hijacking, and spreading of malware, impacting user data privacy and application integrity.

### Details

A user with rights to modificate the service (e.g. kuiperUser role) can inject XSS Payload into Rule `id` parameter. Then, after any user with access to this service (e.g. admin) will try make any modifications with the rule (update, run, stop, delete), a payload will act in victim's browser.

The issue appears as the notification to user is made in an insafe way:

https://github.com/lf-edge/ekuiper/blob/dbce32d5a195cf1de949b3a6a4e29f0df0f3330d/internal/server/rest.go#L681

https://github.com/lf-edge/ekuiper/blob/dbce32d5a195cf1de949b3a6a4e29f0df0f3330d/internal/server/rest.go#L716

https://github.com/lf-edge/ekuiper/blob/dbce32d5a195cf1de949b3a6a4e29f0df0f3330d/internal/server/rest.go#L735

https://github.com/lf-edge/ekuiper/blob/dbce32d5a195cf1de949b3a6a4e29f0df0f3330d/internal/server/rest.go#L794

https://github.com/lf-edge/ekuiper/blob/dbce32d5a195cf1de949b3a6a4e29f0df0f3330d/internal/server/rest.go#L809

https://github.com/lf-edge/ekuiper/blob/dbce32d5a195cf1de949b3a6a4e29f0df0f3330d/internal/server/rest.go#L824

Such writing to 'http.ResponseWriter'  bypasses HTML escaping that prevents cross-site scripting vulnerabilities.

Because of the some (meybe protection) mechanisms a real exploitation is possible only with limited special characters, but this is enough to construct a strong payload

### PoC
1. Create a rule with id:
```
<iframe src="javascript:alert`1337`">
```
![Creating a malicious Rule](https://github.com/user-attachments/assets/32d4f632-1f3c-471a-857b-7c4ce41030c6)

2. Just after Rule Submition the Payload shoots:

![Running Payload](https://github.com/user-attachments/assets/81021d04-e9a4-4e7f-8644-5240dcd2324c)

3. Then, when another user (e.g. `admin`) will try to do something with this rule (e.g. start), the payload shoots in his context:

![Exploiting the admin](https://github.com/user-attachments/assets/9adf9a33-966e-415a-a613-99a9b6cd4f10)

### Impact

Stored Cross-site Scripting (XSS) vulnerability

Reported by Alexey Kosmachev, Lead Pentester from Bi.Zone

## References
- https://github.com/lf-edge/ekuiper/security/advisories/GHSA-6hrw-x7pr-4mp8
- https://nvd.nist.gov/vuln/detail/CVE-2024-52812
- https://github.com/lf-edge/ekuiper
- https://github.com/lf-edge/ekuiper/blob/dbce32d5a195cf1de949b3a6a4e29f0df0f3330d/internal/server/rest.go#L681
- https://github.com/lf-edge/ekuiper/blob/dbce32d5a195cf1de949b3a6a4e29f0df0f3330d/internal/server/rest.go#L716
- https://github.com/lf-edge/ekuiper/blob/dbce32d5a195cf1de949b3a6a4e29f0df0f3330d/internal/server/rest.go#L735
- https://github.com/lf-edge/ekuiper/blob/dbce32d5a195cf1de949b3a6a4e29f0df0f3330d/internal/server/rest.go#L794
- https://github.com/lf-edge/ekuiper/blob/dbce32d5a195cf1de949b3a6a4e29f0df0f3330d/internal/server/rest.go#L809
- https://github.com/lf-edge/ekuiper/blob/dbce32d5a195cf1de949b3a6a4e29f0df0f3330d/internal/server/rest.go#L824
- https://github.com/lf-edge/ekuiper/releases/tag/v2.0.8
- https://pkg.go.dev/vuln/GO-2025-3508
