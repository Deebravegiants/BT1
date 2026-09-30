# [H] IncusOS has a LUKS encryption bypass due to insufficient TPM policy

## Summary
Severity: High
Advisory: GHSA-wj2j-qwcf-cfcc
CVE: CVE-2026-32606
CWE: CWE-522
Ecosystem: Go
CVSS: CVSS:3.1/AV:P/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-03-16
Source: https://github.com/advisories/GHSA-wj2j-qwcf-cfcc
Type: github-advisory

## Affected
- Go: `github.com/lxc/incus-os/incus-osd` — affected >=0 <0.0.0-20260313012803-e3b35f230d23

## Details
The default configuration of systemd-cryptenroll as used by IncusOS through mkosi allows for an attacker with physical access to the machine to access the encrypted data without requiring any interaction by the system's owner or any tampering of Secure Boot state or kernel (UKI) boot image.

That's because in this configuration, the LUKS key is made available by the TPM so long as the system has the expected PCR7 value and the PCR11 policy matches. That default PCR11 policy importantly allows for the TPM to release the key to the booted system rather than just from the initrd part of the signed kernel image (UKI).

The attack relies on the attacker being able to substitute the original encrypted root partition for one that they control. By doing so, the system will prompt for a recovery key on boot, which the attacker has defined and can provide, before booting the system using the attacker's root partition rather than the system's original one.

The attacker only needs to put a systemd unit starting on system boot within their root partition to have the system run that logic on boot. That unit will then run in an environment where the TPM will allow for the retrieval of the encryption key of the real root disk, allowing the attacker to steal the LUKS volume key (immutable master key) and then use it against the real root disk, altering it or getting data out before putting the disk back the way it was and returning the system without a trace of this attack having happened.

This is all possible because the system will have still booted with Secure Boot enabled, will have measured and ran the expected bootloader and kernel image (UKI). The initrd selects the root disk based on GPT partition identifiers making it possible to easily substitute the real root disk for an attacker controlled one. This doesn't lead to any change in the TPM state and therefore allows for retrieval of the LUKS key by the attacker through a boot time systemd unit on their alternative root partition.

Reproducing steps are effectively:
 - Shutdown the system
 - Alter the GPT partition table to remove the GPT type UUID from the root partition
 - Resize the ESP partition to make space for the attacker's own root partition
 - Create a new LUKS encrypted ext4 partition in the space that was freed up and set the GPT type UUID to that of the original root partition
 - Populate that new root partition with a systemd unit and script which use `systemd-cryptenroll` to unlock and extract the key from the original root partition
 - Boot the system
 - When prompted, enter the passphrase of the new (attacker) root partition
 - Let the system boot IncusOS
 - Stop the system
 - Recover the encryption key that was extracted by the boot time systemd unit
 - Access the original root partition using it, steal or modify the data
 - Remove the new (attacker) root partition
 - Grow back the ESP
 - Restore the GPT type UUID on the root partition
 - Start the system back up, it will boot as expected with no indication that it was compromised

### Impact
This impacts all IncusOS users and is a particular worry for anyone running IncusOS in an unsecured physical environment where the system can be tempered with while stopped or is at risk of being seized or stolen.

### Mitigation
The fix we've put in place makes use of PCR15 in addition to the existing PCR7 and PCR11 policies (and PCR4 when running without UEFI Secure Boot). This is significant as PCR15 measures a number of values during system boot, including a measurement of decrypting the root partition while in the initrd.

By binding the LUKS key(s) to an uninitialized PCR15 value, we ensure that only the initrd will be able to automatically decrypt the partitions. As soon as the system boot exits the initrd, whether to boot the legitimate root disk or an attacker's root disk, the TPM state will no longer align with the state required to release the encryption keys, preventing this attack.

https://github.com/lxc/incus-os/pull/954 implements the new logic in IncusOS.

### Future improvements
We've had to use PCR15 directly as a way to prevent this attack as unfortunately mkosi doesn't currently support passing the `phase` option to `ukify`. The `phase` option would allow for a different PCR11 policy to be generated which allows for restricting key access only until the end of the initrd execution.

Being able to use this mechanism would provide a cleaner/simpler solution but it's not currently possible due to lack of mkosi support.

https://github.com/systemd/mkosi/issues/4109

### Patches
IncusOS version 202603142010 (2026/03/14 20:10 UTC)  includes the new PCR15 logic and will automatically update the TPM policy on boot.

Anyone suspecting that their system may have been physically accessed while shut down should perform a full system wipe and reinstallation as only that will rotate the LUKS volume key and prevent subsequent access to the encrypted data should the system have been previously compromised.

### Workarounds
There are no known workarounds other than updating to a version with corrected logic which will automatically rebind the LUKS keys to the new set of TPM registers and prevent this from being exploited.

### Thanks
This was brought to our attention by Linux Containers forum user `U-00F8` who referenced a public January 2025 article by `oddlama` describing a similar attack on systems using the default systemd-cryptenroll setup.

We'd also like to thank Lennart Poettering for his assistance in finding a way to quickly mitigate this attack.

## References
- https://github.com/lxc/incus-os/security/advisories/GHSA-wj2j-qwcf-cfcc
- https://nvd.nist.gov/vuln/detail/CVE-2026-32606
- https://github.com/lxc/incus-os/pull/954
- https://github.com/lxc/incus-os/commit/e3b35f230d23443d27752eac27ebb2b22c957b75
- https://discuss.linuxcontainers.org/t/potential-luks-encryption-bypass-through-filesystem-confusion/26348
- https://github.com/lxc/incus-os
- https://oddlama.org/blog/bypassing-disk-encryption-with-tpm2-unlock
