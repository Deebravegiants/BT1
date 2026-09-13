# [C] CVE-2021-44079

## Summary
Severity: Critical
Advisory: CVE-2021-44079
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-11-22
Source: https://osv.dev/vulnerability/CVE-2021-44079
Type: osv

## Details
In the wazuh-slack active response script in Wazuh 4.2.x before 4.2.5, untrusted user agents are passed to a curl command line, potentially resulting in remote code execution.

## References
- https://github.com/wazuh/wazuh/issues/10858
- https://github.com/wazuh/wazuh/issues/10858#issuecomment-991118254
- https://github.com/wazuh/wazuh/pull/10809
