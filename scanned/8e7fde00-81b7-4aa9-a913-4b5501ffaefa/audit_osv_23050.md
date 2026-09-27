# [H] CVE-2022-42717

## Summary
Severity: High
Advisory: CVE-2022-42717
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-10-11
Source: https://osv.dev/vulnerability/CVE-2022-42717
Type: osv

## Details
An issue was discovered in Hashicorp Packer before 2.3.1. The recommended sudoers configuration for Vagrant on Linux is insecure. If the host has been configured according to this documentation, non-privileged users on the host can leverage a wildcard in the sudoers configuration to execute arbitrary commands as root.

## References
- https://discuss.hashicorp.com/t/hcsec-2022-23-vagrant-nfs-sudoers-configuration-allows-for-local-privilege-escalation/45423
- https://www.vagrantup.com/docs/synced-folders/nfs
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/42xxx/CVE-2022-42717.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-42717
- https://github.com/hashicorp/vagrant/pull/12910
