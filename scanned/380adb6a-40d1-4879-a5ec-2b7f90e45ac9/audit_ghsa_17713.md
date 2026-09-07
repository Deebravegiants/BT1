# [H] Pimcore Authenticated Stored Cross-Site Scripting (XSS) Via Search Document

## Summary
Severity: High
Advisory: GHSA-xr3m-6gq6-22cg
CVE: CVE-2024-11954
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2025-01-28
Source: https://github.com/advisories/GHSA-xr3m-6gq6-22cg
Type: github-advisory

## Affected
- Packagist: `pimcore/pimcore` — affected >=11.4.2 <11.5.3

## Details
### Summary
 
A Stored Cross-Site Scripting (XSS) vulnerability in PIMCORE allows remote attackers to inject arbitrary web script or HTML via the PDF upload functionality. This can result in the execution of malicious scripts in the context of the user's browser when the PDF is viewed, leading to potential session hijacking, defacement of web pages, or unauthorized access to sensitive information.
 
### Details
 
The vulnerability is present in the PDF upload functionality of the PIM Core Upload module. When a user uploads a PDF file, the application fails to properly sanitize the content, allowing embedded scripts to be executed when the PDF is viewed. The affected code is located in the file handling and rendering logic of the PDF upload feature.
 
### PoC
 

 
1. Log in as Administrator
![image](https://github.com/user-attachments/assets/7945bbd7-5277-4a0e-8365-56e5df319bae)

2. Hover to Assets
![image](https://github.com/user-attachments/assets/f24645ee-d740-4a5e-81d1-b8bf48b71cce)

 
3. Right click and click "Add Asset(s) > upload files
![image](https://github.com/user-attachments/assets/0603cc90-44d8-423e-a01c-b0367fd929bd)

 
4. Upload malicious pdf
![image](https://github.com/user-attachments/assets/51aa609d-f100-4f46-b3bb-3d730e000a02)

 
5. Click on search and select document
![image](https://github.com/user-attachments/assets/7e945b26-4f8a-4e91-adea-8f46a0f17856)

 
6. copy the path and open to a new tab 

[https://demo.pimcore.fun/admin/Sample C](https://demo.pimcore.fun/Sample%20Content/Documents/xssmaeitsec.pdf)
 
![image](https://github.com/user-attachments/assets/500d49d6-42f7-4b64-8b01-117f439ace8d)

7. XSS PDF can be access without authentication. 

 
![image](https://github.com/user-attachments/assets/7fb53fc2-2f65-42b3-9ed7-fc0413211a3f)

 Image showing no cookies indicator that there are no session currently in
 
![image](https://github.com/user-attachments/assets/89f58fff-0dee-4520-9071-efd024c2f6d3)

### Impact
This is a Stored Cross-Site Scripting (XSS) vulnerability. It impacts any user who views the malicious PDF, potentially leading to session hijacking, defacement of web pages, or unauthorized access to sensitive information. The severity is high due to the potential for significant impact on confidentiality and integrity.

## References
- https://github.com/pimcore/pimcore/security/advisories/GHSA-xr3m-6gq6-22cg
- https://nvd.nist.gov/vuln/detail/CVE-2024-11954
- https://github.com/pimcore/pimcore
- https://vuldb.com/?ctiid.293905
