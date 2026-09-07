# [M] coreos-installer < 0.10.0 writes world-readable Ignition config to installed system

## Summary
Severity: Medium
Advisory: GHSA-862g-9h5m-m3qv
CVE: CVE-2021-3917
CWE: CWE-276
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2021-11-08
Source: https://github.com/advisories/GHSA-862g-9h5m-m3qv
Type: github-advisory

## Affected
- crates.io: `coreos-installer` — affected >=0 <0.10.0

## Details
### Impact
On systems installed with coreos-installer before 0.10.0, the user-provided Ignition config was written to `/boot/ignition/config.ign` with world-readable permissions, granting unprivileged users access to any secrets included in the config.

Default configurations of Fedora CoreOS and RHEL CoreOS do not include any unprivileged user accounts.  In addition, instances launched from a cloud image, and systems provisioned with the `ignition.config.url` kernel argument, do not use the `config.ign` file and are unaffected.

### Patches
coreos-installer 0.10.0 and later [writes](https://github.com/coreos/coreos-installer/pull/571) the Ignition config with restricted permissions.

### Workarounds

On Fedora CoreOS systems installed from version 34.20210711.3.0 (stable), 34.20210711.2.0 (testing), 34.20210711.1.1 (next) and later, the `/boot/ignition` directory and its contents are removed after provisioning is complete. All Fedora CoreOS systems that have updated to these versions or later have automatically removed the `/boot/ignition` directory and no action is required.

On other systems, `/boot/ignition/config.ign` can be removed manually, as it is not used after provisioning is complete:

```
sudo mount -o remount,rw /boot
sudo rm -rf /boot/ignition
```

### References
For more information, see https://github.com/coreos/fedora-coreos-tracker/issues/889.

### For more information
If you have any questions or comments about this advisory, [open an issue in coreos-installer](https://github.com/coreos/coreos-installer/issues/new/choose) or email the CoreOS [development mailing list](https://lists.fedoraproject.org/archives/list/coreos@lists.fedoraproject.org/).

## References
- https://github.com/coreos/coreos-installer/security/advisories/GHSA-862g-9h5m-m3qv
- https://nvd.nist.gov/vuln/detail/CVE-2021-3917
- https://github.com/coreos/fedora-coreos-tracker/issues/889
- https://github.com/coreos/coreos-installer/commit/2a36405339c87b16ed6c76e91ad5b76638fbdb0c
- https://access.redhat.com/security/cve/CVE-2021-3917
- https://bugzilla.redhat.com/show_bug.cgi?id=2018478
- https://github.com/coreos/coreos-installer
- https://github.com/coreos/coreos-installer/releases/tag/v0.10.0
