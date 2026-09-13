# [H] timber/timber vulnerable to Deserialization of Untrusted Data

## Summary
Severity: High
Advisory: GHSA-6363-v5m4-fvq3
CVE: CVE-2024-29800
CWE: CWE-502, CWE-73
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:H/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2024-04-12
Source: https://github.com/advisories/GHSA-6363-v5m4-fvq3
Type: github-advisory

## Affected
- Packagist: `timber/timber` — affected >=2.0.0 <2.1.0
- Packagist: `timber/timber` — affected >=1.24.0 <1.24.1
- Packagist: `timber/timber` — affected >=0.16.6 <1.23.1

## Details
### Summary
Timber is vulnerable to PHAR deserialization due to a lack of checking the input before passing it into the file_exists() function. If an attacker can upload files of any type to the server, he can pass in the phar:// protocol to unserialize the uploaded file and instantiate arbitrary PHP objects. This can lead to remote code execution especially when Timber is used with frameworks with documented POP chains like Wordpress/ vulnerable developer code.

### Details
The vulnerability lies in the run function within the toJpg.php file. The two parameters passed into it are not checked or sanitized, hence an attacker could potentially inject malicious input leading to Deserialization of Untrusted Data, allowing for remote code execution:
![image](https://github.com/timber/timber/assets/89630690/bcd6d031-33c6-4cc5-96b7-b72f0cf0e26c)

### PoC
Setup the following code in /var/www/html: vuln.php represents our use of Timber functions and phar-poc.php represents code with a vulnerable POP chain.
![image](https://github.com/timber/timber/assets/89630690/967f0a16-3b7e-4b58-84cb-c1dee3291339)
![image](https://github.com/timber/timber/assets/89630690/78bb98cf-0cd2-4635-aa01-a1eea571d0fc)
As an attacker, we generate our PHAR payload using the following exploit script:
![image](https://github.com/timber/timber/assets/89630690/d823e76a-fb07-468e-aed1-97b304d53ee5)
Generate with:
![image](https://github.com/timber/timber/assets/89630690/d3d57333-a113-468a-8b27-dc6bc1fca4e7)
then change extension file from .phar to valid extension as svg,jpg,...
![image](https://github.com/timber/timber/assets/89630690/c4fdbd25-e828-4408-9feb-168f2e301d7a)
and execute vuln.php with php vuln.php, you should see whoami being executed:
![image](https://github.com/timber/timber/assets/89630690/e341de8d-555c-4390-86a1-469b11cf0ffc)
![image](https://github.com/timber/timber/assets/89630690/17afdb95-10ed-4c52-a93d-95eb1f60a146)

### Impact
This vulnerability is capable of remote code execution if Timber is used with frameworks or developer code with vulnerable POP chains.

### Recommended Fix
Filter the phar:// protocol.

## References
- https://github.com/timber/timber/security/advisories/GHSA-6363-v5m4-fvq3
- https://github.com/timber/timber/issues/2971
- https://github.com/timber/timber/commit/13c6b0f60346304f2eed4da1e0bb51566518de4a
- https://github.com/FriendsOfPHP/security-advisories/blob/master/timber/timber/CVE-2024-29800.yaml
- https://github.com/timber/timber
