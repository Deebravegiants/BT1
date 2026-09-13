# [M] LobeHub Vulnerable to Improper Authorization in Presigned Upload

## Summary
Severity: Medium
Advisory: GHSA-wrrr-8jcv-wjf5
CVE: CVE-2026-23835
CWE: CWE-73
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:H/VA:H/SC:N/SI:N/SA:N/E:P (CVSS_V4)
Published: 2026-02-01
Source: https://github.com/advisories/GHSA-wrrr-8jcv-wjf5
Type: github-advisory

## Affected
- npm: `@lobehub/chat` — affected >=0 <1.143.3

## Details
### Summary
The file upload feature in `Knowledge Base > File Upload` does not validate the integrity of the upload request, allowing users to intercept and modify the request parameters. As a result, it is possible to create arbitrary files in abnormal or unintended paths. In addition, since `lobechat.com` relies on the size parameter from the request to calculate file usage, an attacker can manipulate this value to misrepresent the actual file size, such as uploading a `1 GB` file while reporting it as `10 MB`, or falsely declaring a `10 MB` file as a `1 GB` file.

### Details
After entering the Knowledge Base, click the file upload option and upload any file. At this point, use a tool such as Burp Suite to intercept and inspect the request sent to `POST /trpc/lambda/file.createFile?batch=1` (the request packet is shown in the image below). By modifying the name and size fields in this request, it is possible to bypass the maximum upload size enforced by LobeChat’s monthly subscription plan and upload files beyond the intended service storage limits.
<img width="670" height="413" alt="image" src="https://github.com/user-attachments/assets/c83cfb81-3bcc-4562-b052-5344ccf6356f" />

### Impacts
By manipulating the size value provided in the client upload request, it is possible to bypass the monthly upload quota enforced by the server and continuously upload files beyond the intended storage and traffic limits. This abuse can result in a discrepancy between actual resource consumption and billing calculations, causing direct financial impact to the service operator. Additionally, exhaustion of storage or related resources may lead to degraded service availability, including failed uploads, delayed content delivery, or temporary suspension of upload functionality for legitimate users. A single malicious user can also negatively affect other users or projects sharing the same subscription plan, effectively causing an indirect denial of service (DoS). Furthermore, excessive and unaccounted-for uploads can distort monitoring metrics and overload downstream systems such as backup processes, malware scanning, and media processing pipelines, ultimately undermining overall operational stability and service reliability

### PoC
<img width="572" height="498" alt="image" src="https://github.com/user-attachments/assets/cb5d4a7d-513c-49bf-a75b-0e6abb7f144a" />
<img width="887" height="305" alt="image" src="https://github.com/user-attachments/assets/31d80889-d169-45af-b052-f7f4b5f654da" />
<img width="286" height="95" alt="image" src="https://github.com/user-attachments/assets/0a112966-cb3c-4045-af85-acad9f645056" />

<img width="568" height="503" alt="image" src="https://github.com/user-attachments/assets/51cfa49e-ffef-4e04-be3e-77a67d41e1c0" />
<img width="602" height="275" alt="image" src="https://github.com/user-attachments/assets/d0b5a85d-60bc-4ffe-9877-1dca989dfe92" />
<img width="281" height="106" alt="image" src="https://github.com/user-attachments/assets/fc68eaeb-b320-4066-80f8-18aa6e42cdaf" />

## References
- https://github.com/lobehub/lobehub/security/advisories/GHSA-wrrr-8jcv-wjf5
- https://nvd.nist.gov/vuln/detail/CVE-2026-23835
- https://github.com/lobehub/lobehub/commit/2c1762b85acb84467ed5e799afe1499cd2f912e6
- https://github.com/lobehub/lobehub
