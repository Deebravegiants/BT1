# [M] nitro-tpm-pcr-compute may allow kernel command line modification by an account operator

## Summary
Severity: Medium
Advisory: GHSA-xrv8-2pf5-f3q7
CWE: CWE-77
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2025-12-05
Source: https://github.com/advisories/GHSA-xrv8-2pf5-f3q7
Type: github-advisory

## Affected
- crates.io: `nitro-tpm-pcr-compute` — affected >=0 <1.1.0

## Details
## Summary

Adding default PCR12 validation to ensure that account operators can not modify kernel command line parameters, potentially bypassing root filesystem integrity validation.

Attestable AMIs are based on the systemd Unified Kernel Image (UKI) concept which uses systemd-boot to create a single measured UEFI binary from a Linux kernel, its initramfs, and kernel command line. The embedded kernel command line contains a dm-verity hash value that establishes trust in the root file system.

When UEFI Secure Boot is disabled, systemd-boot appends any command line it receives to the kernel command line. Account operators with the ability to modify UefiData can install a boot variable with a command line that deactivates root file system integrity validation, while preserving the original PCR4 value.

Systemd-boot provides separate measurement of command line modifications in PCR12.

## Impact

In line with the TPM 2.0 specification and systemd-stub logic, KMS policies that do not include validation for PCR12 (command line measurement) or PCR7 (enabled Secure Boot) may allow kernel command line modification by an account operator.

## Patches 

Version 1.1.0 of nitro-tpm-pcr-compute has been updated to include PCR12 with a static zero value. The updated tool now outputs PCR12 in the JSON measurements:

```json
{
  "Measurements": {
    "HashAlgorithm": "SHA384",
    "PCR4": "<hex string>",
    "PCR7": "<hex string>",
    "PCR12": "000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000"
  }
}
```

## Workarounds

For users who cannot upgrade to version 1.1.0 of nitro-tpm-pcr-compute immediately, the following workarounds are available:

1. **Manually add PCR12 to KMS policies:** Add PCR12 with a static zero value to your AWS KMS key policies:

```txt
kms:RecipientAttestation:NitroTPMPCR12:000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
```

2. **Enable and validate UEFI Secure Boot:** Configure your Attestable AMI to use UEFI Secure Boot and validate its enablement via PCR7 in your KMS policy. When UEFI Secure Boot is active, the command line cannot be overwritten.

## References
- https://github.com/aws/nitrotpm-attestation-samples/security/advisories/GHSA-xrv8-2pf5-f3q7
- https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/attestable-ami.html
- https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/uefi-secure-boot.html
- https://github.com/aws/NitroTPM-Tools
- https://github.com/aws/NitroTPM-Tools/blob/main/CHANGELOG.md
- https://github.com/aws/NitroTPM-Tools/releases/tag/v1.1.0
- https://github.com/aws/nitrotpm-attestation-samples
- https://www.freedesktop.org/software/systemd/man/latest/systemd-stub.html
