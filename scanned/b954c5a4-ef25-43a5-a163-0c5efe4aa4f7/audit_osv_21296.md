# [M] CVE-2021-41821

## Summary
Severity: Medium
Advisory: CVE-2021-41821
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-09-29
Source: https://osv.dev/vulnerability/CVE-2021-41821
Type: osv

## Details
Wazuh Manager in Wazuh through 4.1.5 is affected by a remote Integer Underflow vulnerability that might lead to denial of service. A crafted message must be sent from an authenticated agent to the manager.

## References
- https://documentation.wazuh.com/current/release-notes/release_4_2_0.html
- https://github.com/wazuh/wazuh/issues/9201
