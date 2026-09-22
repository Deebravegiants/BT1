# [H] CVE-2023-20900

## Summary
Severity: High
Advisory: CVE-2023-20900
CVSS: 7.5 (CVSS:3.1/AV:A/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-08-31
Source: https://osv.dev/vulnerability/CVE-2023-20900
Type: osv

## Details
A malicious actor that has been granted  Guest Operation Privileges https://docs.vmware.com/en/VMware-vSphere/8.0/vsphere-security/GUID-6A952214-0E5E-4CCF-9D2A-90948FF643EC.html  in a target virtual machine may be able to elevate their privileges if that target virtual machine has been assigned a more privileged  Guest Alias https://vdc-download.vmware.com/vmwb-repository/dcr-public/d1902b0e-d479-46bf-8ac9-cee0e31e8ec0/07ce8dbd-db48-4261-9b8f-c6d3ad8ba472/vim.vm.guest.AliasManager.html .

## References
- http://www.openwall.com/lists/oss-security/2023/08/31/1
- https://www.debian.org/security/2023/dsa-5493
- https://security.netapp.com/advisory/ntap-20231013-0002/
- http://www.openwall.com/lists/oss-security/2023/10/27/1
- https://www.vmware.com/security/advisories/VMSA-2023-0019.html
- https://lists.debian.org/debian-lts-announce/2023/10/msg00000.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/NVKQ6Y2JFJRWPFOZUOTFO3H27BK5GGOG/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/TJNJMD67QIT6LXLKWSHFM47DCLRSMT6W/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/ZJM6HDRQYS74JA7YNKQBFH2XSZ52HEWH/
