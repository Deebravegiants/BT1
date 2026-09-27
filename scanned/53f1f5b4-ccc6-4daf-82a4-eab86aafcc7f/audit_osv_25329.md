# [H] CVE-2023-34058

## Summary
Severity: High
Advisory: CVE-2023-34058
CVSS: 7.1 (CVSS:3.1/AV:A/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-10-27
Source: https://osv.dev/vulnerability/CVE-2023-34058
Type: osv

## Details
VMware Tools contains a SAML token signature bypass vulnerability. A malicious actor that has been granted  Guest Operation Privileges https://docs.vmware.com/en/VMware-vSphere/8.0/vsphere-security/GUID-6A952214-0E5E-4CCF-9D2A-90948FF643EC.html  in a target virtual machine may be able to elevate their privileges if that target virtual machine has been assigned a more privileged  Guest Alias https://vdc-download.vmware.com/vmwb-repository/dcr-public/d1902b0e-d479-46bf-8ac9-cee0e31e8ec0/07ce8dbd-db48-4261-9b8f-c6d3ad8ba472/vim.vm.guest.AliasManager.html .

## References
- http://www.openwall.com/lists/oss-security/2023/10/27/1
- https://lists.debian.org/debian-lts-announce/2023/11/msg00002.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/G7G77Z76CQPGUF7VHRA6O3UFCMPPR4O2/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/MQUOFQL2SNNNMKROQ3TZQY4HEYMNOIBW/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/WLTKVTRKQW2GD2274H3UOW6XU4E62GSK/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/34xxx/CVE-2023-34058.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-34058
- https://www.debian.org/security/2023/dsa-5543
- https://www.vmware.com/security/advisories/VMSA-2023-0024.html
