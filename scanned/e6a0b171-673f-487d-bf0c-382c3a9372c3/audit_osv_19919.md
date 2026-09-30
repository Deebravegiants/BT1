# [M] CVE-2021-27904

## Summary
Severity: Medium
Advisory: CVE-2021-27904
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2021-03-02
Source: https://osv.dev/vulnerability/CVE-2021-27904
Type: osv

## Details
An issue was discovered in app/Model/SharingGroupServer.php in MISP 2.4.139. In the implementation of Sharing Groups, the "all org" flag sometimes provided view access to unintended actors.

## References
- https://github.com/MISP/MISP/commit/ca13fee271ad126832c88896776f3050a6c06e64
