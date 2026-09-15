# [H] CVE-2024-34477

## Summary
Severity: High
Advisory: CVE-2024-34477
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-27
Source: https://osv.dev/vulnerability/CVE-2024-34477
Type: osv

## Details
configureNFS in lib/common/functions.sh in FOG through 1.5.10 allows local users to gain privileges by mounting a crafted NFS share (because of no_root_squash and insecure). In order to exploit the vulnerability, someone needs to mount an NFS share in order to add an executable file as root. In addition, the SUID bit must be added to this file.

## References
- https://forums.fogproject.org/topic/17486/fog-1-5-10-and-earlier-nfs-privilege-escalation-vulnerability
- https://github.com/FOGProject/fogproject/blob/a4bb1bf39ac53c3cbe623576915fbc3b5c80a00f/lib/common/functions.sh#L1360
- https://blog.hackvens.fr/advisories/CVE-2024-34477-Fogproject.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/34xxx/CVE-2024-34477.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-34477
