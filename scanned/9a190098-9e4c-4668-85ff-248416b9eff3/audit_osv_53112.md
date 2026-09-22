# [M] CVE-2022-29799

## Summary
Severity: Medium
Advisory: CVE-2022-29799
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2022-09-21
Source: https://osv.dev/vulnerability/CVE-2022-29799
Type: osv

## Details
A vulnerability was found in networkd-dispatcher. This flaw exists because no functions are sanitized by the OperationalState or the AdministrativeState of networkd-dispatcher. This attack leads to a directory traversal to escape from the “/etc/networkd-dispatcher” base directory.

## References
- https://www.microsoft.com/security/blog/2022/04/26/microsoft-finds-new-elevation-of-privilege-linux-vulnerability-nimbuspwn/
- https://www.microsoft.com/security/blog/2022/04/26/microsoft-finds-new-elevation-of-privilege-linux-vulnerability-nimbuspwn/
- https://www.microsoft.com/security/blog/2022/04/26/microsoft-finds-new-elevation-of-privilege-linux-vulnerability-nimbuspwn/
- https://www.microsoft.com/security/blog/2022/04/26/microsoft-finds-new-elevation-of-privilege-linux-vulnerability-nimbuspwn/
