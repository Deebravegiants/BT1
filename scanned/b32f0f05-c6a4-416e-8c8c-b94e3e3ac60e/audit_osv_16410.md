# [M] CVE-2019-6512

## Summary
Severity: Medium
Advisory: CVE-2019-6512
CVSS: 4.1 (CVSS:3.0/AV:N/AC:L/PR:H/UI:N/S:C/C:L/I:N/A:N)
Published: 2019-05-14
Source: https://osv.dev/vulnerability/CVE-2019-6512
Type: osv

## Details
An issue was discovered in WSO2 API Manager 2.6.0. It is possible to force the application to perform requests to the internal workstation (SSRF port-scanning), other adjacent workstations (SSRF network scanning), or to enumerate files because of the existence of the file:// wrapper.

## References
- https://cds.thalesgroup.com/en/tcs-cert/CVE-2019-6512
- https://wso2.com/security-patch-releases/api-manager
- https://www.excellium-services.com/cert-xlm-advisory
