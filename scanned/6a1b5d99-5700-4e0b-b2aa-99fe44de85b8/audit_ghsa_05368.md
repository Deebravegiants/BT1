# [C] Harvest May Expose OS Default SSH Login Password Via SUSE Virtualization Interactive Installer

## Summary
Severity: Critical
Advisory: GHSA-6g8q-hp2j-gvwv
CVE: CVE-2025-62877
CWE: CWE-1188
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-01-05
Source: https://github.com/advisories/GHSA-6g8q-hp2j-gvwv
Type: github-advisory

## Affected
- Go: `github.com/harvester/harvester-installer` — affected >=1.6.0
- Go: `github.com/harvester/harvester-installer` — affected >=1.5.0

## Details
### Impact

Projects using the SUSE Virtualization (Harvester) environment are vulnerable to this exploit if they are using the 1.5.x or 1.6.x interactive installer to either create a new cluster or add new hosts to an existing cluster.  The environment is not affected if the [PXE boot mechanism](https://docs.harvesterhci.io/v1.7/install/pxe-boot-install/) is utilized along with the [Harvester configuration](https://docs.harvesterhci. io/v1.7/install/harvester-configuration) setup.

A critical vulnerability has been identified within the SUSE Virtualization interactive installer. This vulnerability allows an attacker to gain unauthorized network access to the host via a remote shell (SSH).

The SUSE Virtualization operating system includes a default administrative login credential intended solely for out-of-band cluster management tasks (for example, perform troubleshooting, device management and system recovery over serial ports). When the interactive installer is used to create or expand a cluster, the installer enables the host's networking functions before the default password is reset. This presents a window of opportunity for an attacker to exploit the default password to gain unauthorized access to the host via SSH. 

Please consult the associated  [MITRE ATT&CK - Technique - Default Credentials](https://attack.mitre.org/techniques/T0812/) for further information about this category of attack.

### Patches

This vulnerability is addressed by updating the interactive installer to allow the user to reset the OS default login password, before proceeding to other system configuration screens like the host networking screen and before network connectivity for remote access to the host is actually enabled. 

v1.7.0 and later include the necessary security fixes. 

### Workarounds

For environments that are dependent on the SUSE Virtualization 1.5 and 1.6 interactive installer, users should upgrade the clusters to SUSE Virtualization 1.7 and use the 1.7 installer to manage hosts. These versions allow users to reset the operating system's default administrative password before proceeding to other system configuration screens and before enabling network connectivity for remote host access.

Projects can also perform one of the following workarounds to mitigate the risk:

* If upgrading to v1.7.x is not an option, use the [PXE boot mechanism](https://docs.harvesterhci.io/v1.7/install/pxe-boot-install/) along with a configuration file to define a secure password. 
* Apply network security controls to limit access to the server from any untrusted location during bootstrapping. For example, ensure that port 22 is not exposed to the public internet until at least the default login password is changed to a secure value.

### Resources

If users have any questions or comments about this advisory: 
* Reach out to the [SUSE Rancher Security team](https://github.com/harvester/harvester/security/policy) for security related inquiries.
* Open an issue in the [Harvester](https://github.com/harvester/harvester/issues/new/choose) repository.
* Verify with the [support matrix](https://www.suse.com/suse-harvester/support-matrix/all-supported-versions/harvester-v1-6-x/) and [product support lifecycle](https://www.suse.com/lifecycle/#suse-virtualization).

## References
- https://github.com/harvester/harvester/security/advisories/GHSA-6g8q-hp2j-gvwv
- https://nvd.nist.gov/vuln/detail/CVE-2025-62877
- https://bugzilla.suse.com/show_bug.cgi?id=CVE-2025-62877
- https://github.com/harvester/harvester
