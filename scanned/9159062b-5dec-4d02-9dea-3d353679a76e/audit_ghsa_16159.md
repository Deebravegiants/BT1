# [H] Craft CMS Arbitrary System File Read

## Summary
Severity: High
Advisory: GHSA-cw6g-qmjq-6w2w
CVE: CVE-2024-52292
CWE: CWE-22, CWE-552
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2024-11-13
Source: https://github.com/advisories/GHSA-cw6g-qmjq-6w2w
Type: github-advisory

## Affected
- Packagist: `craftcms/cms` — affected >=5.0.0-alpha.1 <5.4.9
- Packagist: `craftcms/cms` — affected >=3.5.13 <4.12.8

## Details
### Summary
By abusing the mail notification template it is possible to read arbitrary operating system files. 

### Details
The [dataUrl](https://craftcms.com/docs/3.x/dev/functions.html#dataurl) function can be exploited if an attacker has write permissions on system notification templates. This function accepts an absolute file path, reads the file's content, and converts it into a Base64-encoded string. By embedding this function within a system notification template, the attacker can exfiltrate the Base64-encoded file content through a triggered system email notification. Once the email is received, the Base64 payload can be decoded, allowing the attacker to read arbitrary files on the server.

Requirements:
* write permissions to system notification templates
* ability to trigger a corresponding system email

### PoC
1) Modify a template to contain the following twig template string:
```twig
{{ dataUrl('/var/www/web/.env') }}
```
2) Trigger the corresponding notification email (e.g. by resetting a password)
3) Receive the email and decode the base64 string

Mail received:
![Bildschirmfoto 2024-09-05 um 16 20 41](https://github.com/user-attachments/assets/24dc5196-6847-4006-b7ef-8cd10d659c30)

Decoded string:
![Bildschirmfoto 2024-09-05 um 16 28 24](https://github.com/user-attachments/assets/1913a475-5277-49b9-9210-2f3fcd3b9bf1)


### Impact
1) Exposure of Sensitive Information: Arbitrary file read can lead to the exposure of sensitive data such as configuration files (e.g., /etc/passwd, .env, config.php), which may contain credentials, API keys, or database passwords. This can provide the attacker with further access to the system or connected services.

2) Privilege Escalation: If the attacker is able to read files that contain privileged information, such as credentials for other systems or applications, they may be able to escalate their privileges beyond what the web admin role originally allowed, potentially gaining full control over the server or other related systems.

3) Server Compromise: Access to files like SSH keys, private certificates, or system configuration files can lead to the complete compromise of the underlying server. With this information, an attacker could remotely log in to the server or impersonate it in secure communications.

4) Exfiltration of User Data: The ability to read arbitrary files may allow an attacker to access user data, such as stored passwords, session tokens, or private information (like uploaded files or logs), leading to a breach of confidentiality and violating privacy regulations (e.g., GDPR).

## References
- https://github.com/craftcms/cms/security/advisories/GHSA-cw6g-qmjq-6w2w
- https://nvd.nist.gov/vuln/detail/CVE-2024-52292
- https://github.com/craftcms/cms
