# [C] CVE-2024-36622

## Summary
Severity: Critical
Advisory: CVE-2024-36622
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-11-29
Source: https://osv.dev/vulnerability/CVE-2024-36622
Type: osv

## Details
In RaspAP raspap-webgui 3.0.9 and earlier, a command injection vulnerability exists in the clearlog.php script. The vulnerability is due to improper sanitization of user input passed via the logfile parameter.

## References
- https://gist.github.com/1047524396/ab997b902ec892e592a0df93f38e6941
- https://github.com/RaspAP/raspap-webgui/blob/3.0.9/ajax/logging/clearlog.php
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/36xxx/CVE-2024-36622.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-36622
- https://github.com/raspap/raspap-webgui/commit/c98d2b0c15942b4829d31dec615b9b40cc6faa14#diff-939ee414d82245c3b3dd7d36b57f10706e06e8f0871b24bdcf9de6e0d181c4c9
