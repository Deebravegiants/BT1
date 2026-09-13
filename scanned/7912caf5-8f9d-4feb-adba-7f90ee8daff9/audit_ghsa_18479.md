# [M] HashiCorp Vagrant has code injection vulnerability through default synced folders

## Summary
Severity: Medium
Advisory: GHSA-hqp6-mjw3-f586
CVE: CVE-2025-34075
CWE: CWE-276, CWE-668, CWE-94
Ecosystem: RubyGems
CVSS: CVSS:4.0/AV:L/AC:L/AT:P/PR:L/UI:A/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X (CVSS_V4)
Published: 2025-07-02
Source: https://github.com/advisories/GHSA-hqp6-mjw3-f586
Type: github-advisory

## Affected
- RubyGems: `vagrant` — affected >=2.2.10 <2.4.7

## Details
An authenticated virtual machine escape vulnerability exists in HashiCorp Vagrant versions 2.4.6 and below when using the default synced folder configuration. By design, Vagrant automatically mounts the host system’s project directory into the guest VM under /vagrant (or C:\vagrant on Windows). This includes the Vagrantfile configuration file, which is a Ruby script evaluated by the host every time a vagrant command is executed in the project directory. If a low-privileged attacker obtains shell access to the guest VM, they can append arbitrary Ruby code to the mounted Vagrantfile. When a user on the host later runs any vagrant command, the injected code is executed on the host with that user’s privileges.

While this shared-folder behavior is well-documented by Vagrant, the security implications of Vagrantfile execution from guest-writable storage are not explicitly addressed. This effectively enables guest-to-host code execution in multi-tenant or adversarial VM scenarios.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-34075
- https://github.com/hashicorp/vagrant/issues/13688
- https://github.com/hashicorp/vagrant/commit/abe87b2fdc124ef426c016d44d2f6f4792f0cbe3
- https://developer.hashicorp.com/vagrant
- https://developer.hashicorp.com/vagrant/docs/synced-folders/basic_usage
- https://developer.hashicorp.com/vagrant/docs/vagrantfile
- https://github.com/advisories/GHSA-hqp6-mjw3-f586
- https://github.com/hashicorp/vagrant
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/vagrant/CVE-2025-34075.yml
- https://raw.githubusercontent.com/rapid7/metasploit-framework/master/modules/exploits/multi/local/vagrant_synced_folder_vagrantfile_breakout.rb
- https://vulncheck.com/advisories/hashicorp-vagrant-synced-folder-vagrantfile-breakout
