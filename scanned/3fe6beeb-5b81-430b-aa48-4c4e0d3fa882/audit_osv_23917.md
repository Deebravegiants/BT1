# [H] CVE-2022-4967

## Summary
Severity: High
Advisory: CVE-2022-4967
CVSS: 7.7 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N)
Published: 2024-05-13
Source: https://osv.dev/vulnerability/CVE-2022-4967
Type: osv

## Details
strongSwan versions 5.9.2 through 5.9.5 are affected by authorization bypass through improper validation of certificate with host mismatch (CWE-297). When certificates are used to authenticate clients in TLS-based EAP methods, the IKE or EAP identity supplied by a client is not enforced to be contained in the client's certificate. So clients can authenticate with any trusted certificate and claim an arbitrary IKE/EAP identity as their own. This is problematic if the identity is used to make policy decisions. A fix was released in strongSwan version 5.9.6 in August 2022 (e4b4aabc4996fc61c37deab7858d07bc4d220136).

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/4xxx/CVE-2022-4967.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-4967
- https://security.netapp.com/advisory/ntap-20240614-0006/
- https://www.strongswan.org/blog/2024/05/13/strongswan-vulnerability-(cve-2022-4967).html
- https://www.cve.org/CVERecord?id=CVE-2022-4967
- https://github.com/strongswan/strongswan/commit/e4b4aabc4996fc61c37deab7858d07bc4d220136
- https://github.com/strongswan/strongswan
