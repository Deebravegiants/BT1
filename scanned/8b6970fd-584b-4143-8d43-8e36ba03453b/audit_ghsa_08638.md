# [C] torrentpier has PHP Serialize Injections

## Summary
Severity: Critical
Advisory: GHSA-h29g-c9cx-c73q
CWE: CWE-502
Ecosystem: Packagist
Published: 2026-05-11
Source: https://github.com/advisories/GHSA-h29g-c9cx-c73q
Type: github-advisory

## Affected
- Packagist: `torrentpier/torrentpier` — affected >=0 <2.4.4

## Details
### Summary
Hi, there. We've found PHP Serialize Injections in your project “torrentpier". According to the OWASP, it can pose a significant risk: enable an attacker to modify serialized objects in order to inject malicious data into the application code, resulting in code execution or an arbitrary reading of the file on any vulnerable system. 
                                        
### Details
In the attachment you can find a report with the number of vulnerabilities, their types and the vulnerable files. To view the lines of vulnerable code you may scan your project with the "[PHP Secure](https://phpsecure.net/?utm_source=github&utm_term=torrentpier&utm_content=torrentpier)" vulnerability scanner with a full access to it.

### PoC
<img width="663" alt="Screenshot 2023-09-25 at 11 12 32 AM" src="https://user-images.githubusercontent.com/118765013/270273991-4a2c3884-3ab0-48ad-af77-3f3dbfa64e2a.png">
<img width="661" alt="Screenshot 2023-09-25 at 11 12 43 AM" src="https://user-images.githubusercontent.com/118765013/270274006-247ed9d3-2dc0-4a87-8f1f-89079c8be165.png">
<img width="664" alt="Screenshot 2023-09-25 at 11 12 53 AM" src="https://user-images.githubusercontent.com/118765013/270274018-b99d6ec2-4c5a-439f-b089-9e11345e963d.png">
<img width="662" alt="Screenshot 2023-09-25 at 11 13 13 AM" src="https://user-images.githubusercontent.com/118765013/270274023-36ecffc7-215d-41db-b3ba-6aa677e644d3.png">

### About Us
We are a team of developers of the PHP Secure vulnerability scanner. First, we checked your code automatically. Then we reviewed the vulnerable code more deeply manually and felt it was necessary to report about it to you. We suggest you scanning your code and address vulnerabilities as soon as possible to prevent a potential breach.

If you have any questions, email us at support@phpsecure.net"

## References
- https://github.com/torrentpier/torrentpier/security/advisories/GHSA-h29g-c9cx-c73q
- https://github.com/torrentpier/torrentpier
