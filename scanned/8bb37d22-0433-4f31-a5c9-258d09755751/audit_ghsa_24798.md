# [M] Ignition config accessible to unprivileged software on VMware

## Summary
Severity: Medium
Advisory: GHSA-hj57-j5cw-2mwp
CVE: CVE-2022-1706
CWE: CWE-200, CWE-863, CWE-921
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-25
Source: https://github.com/advisories/GHSA-hj57-j5cw-2mwp
Type: github-advisory

## Affected
- Go: `github.com/coreos/ignition/v2` — affected >=0 <2.14.0
- Go: `github.com/coreos/ignition` — affected >=0 <2.14.0

## Details
### Impact
Unprivileged software in VMware VMs, including software running in unprivileged containers, can retrieve an Ignition config stored in a hypervisor guestinfo variable or OVF environment.  If the Ignition config contains secrets, this can result in the compromise of sensitive information.

### Patches
Ignition 2.14.0 and later [adds](https://github.com/coreos/ignition/pull/1350) a new systemd service, `ignition-delete-config.service`, that deletes the Ignition config from supported hypervisors (currently VMware and VirtualBox) during the first boot.  This ensures that unprivileged software cannot retrieve the Ignition config from the hypervisor.

If you have external tooling that requires the Ignition config to remain accessible in VM metadata after provisioning, and your Ignition config does not include sensitive information, you can prevent Ignition 2.14.0 and later from deleting the config by masking `ignition-delete-config.service`.  For example:

```json
{
  "ignition": {
    "version": "3.0.0"
  },
  "systemd": {
    "units": [
      {
        "name": "ignition-delete-config.service",
        "mask": true
      }
    ]
  }
}
```

### Workarounds
[Avoid storing secrets](https://coreos.github.io/ignition/operator-notes/#secrets) in Ignition configs. In addition to VMware, many cloud platforms allow unprivileged software in a VM to retrieve the Ignition config from a networked cloud metadata service. While platform-specific mitigation is possible, such as firewall rules that prevent access to the metadata service, it's best to store secrets in a dedicated platform such as [Hashicorp Vault](https://www.vaultproject.io/).

### Advice to Linux distributions
Linux distributions that ship Ignition should ensure the new `ignition-delete-config.service` is installed and enabled by default.

In addition, we recommend shipping a service similar to `ignition-delete-config.service` that runs when existing machines are upgraded, similar to the one in https://github.com/coreos/fedora-coreos-config/pull/1738. Consider giving your users advance notice of this change, and providing instructions for masking `ignition-delete-config.service` on existing nodes if users have tooling that requires the Ignition config to remain accessible in VM metadata.

### References
For more information, see #1300 and #1350.

### For more information
If you have any questions or comments about this advisory, [open an issue in Ignition](https://github.com/coreos/ignition/issues/new/choose) or email the CoreOS [development mailing list](https://lists.fedoraproject.org/archives/list/coreos@lists.fedoraproject.org/).

## References
- https://github.com/coreos/ignition/security/advisories/GHSA-hj57-j5cw-2mwp
- https://github.com/coreos/ignition/issues/1300
- https://github.com/coreos/ignition/pull/1350
- https://github.com/coreos/ignition
