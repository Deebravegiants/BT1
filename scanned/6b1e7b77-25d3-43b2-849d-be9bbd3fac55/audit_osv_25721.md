# [M] Samba: "rpcecho" development server allows denial of service via sleep() call on ad dc

## Summary
Severity: Medium
Advisory: CVE-2023-42669
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-11-06
Source: https://osv.dev/vulnerability/CVE-2023-42669
Type: osv

## Details
A vulnerability was found in Samba's "rpcecho" development server, a non-Windows RPC server used to test Samba's DCE/RPC stack elements. This vulnerability stems from an RPC function that can be blocked indefinitely. The issue arises because the "rpcecho" service operates with only one worker in the main RPC task, allowing calls to the "rpcecho" server to be blocked for a specified time, causing service disruptions. This disruption is triggered by a "sleep()" call in the "dcesrv_echo_TestSleep()" function under specific conditions. Authenticated users or attackers can exploit this vulnerability to make calls to the "rpcecho" server, requesting it to block for a specified duration, effectively disrupting most services and leading to a complete denial of service on the AD DC. The DoS affects all other services as "rpcecho" runs in the main RPC task.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://www.samba.org/samba/security/CVE-2023-42669.html
- https://access.redhat.com/errata/RHSA-2023:6209
- https://access.redhat.com/errata/RHSA-2023:6744
- https://access.redhat.com/errata/RHSA-2023:7371
- https://access.redhat.com/errata/RHSA-2023:7408
- https://access.redhat.com/errata/RHSA-2023:7464
- https://access.redhat.com/errata/RHSA-2023:7467
- https://access.redhat.com/security/cve/CVE-2023-42669
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/42xxx/CVE-2023-42669.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-42669
- https://security.netapp.com/advisory/ntap-20231124-0002/
- https://bugzilla.redhat.com/show_bug.cgi?id=2241884
- https://bugzilla.samba.org/show_bug.cgi?id=15474
- https://github.com/samba-team/samba
