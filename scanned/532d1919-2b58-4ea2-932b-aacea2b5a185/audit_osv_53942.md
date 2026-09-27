# [H] CVE-2023-33466

## Summary
Severity: High
Advisory: CVE-2023-33466
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-06-29
Source: https://osv.dev/vulnerability/CVE-2023-33466
Type: osv

## Details
Orthanc before 1.12.0 allows authenticated users with access to the Orthanc API to overwrite arbitrary files on the file system, and in specific deployment scenarios allows the attacker to overwrite the configuration, which can be exploited to trigger Remote Code Execution (RCE).

## References
- https://lists.debian.org/debian-lts-announce/2023/09/msg00009.html
- https://www.debian.org/security/2023/dsa-5473
- https://discourse.orthanc-server.org/t/security-advisory-for-orthanc-deployments-running-versions-before-1-12-0/3568
