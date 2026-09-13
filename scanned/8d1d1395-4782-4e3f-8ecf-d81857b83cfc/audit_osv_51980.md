# [M] CVE-2021-46922

## Summary
Severity: Medium
Advisory: CVE-2021-46922
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-02-27
Source: https://osv.dev/vulnerability/CVE-2021-46922
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

KEYS: trusted: Fix TPM reservation for seal/unseal

The original patch 8c657a0590de ("KEYS: trusted: Reserve TPM for seal
and unseal operations") was correct on the mailing list:

https://lore.kernel.org/linux-integrity/20210128235621.127925-4-jarkko@kernel.org/

But somehow got rebased so that the tpm_try_get_ops() in
tpm2_seal_trusted() got lost.  This causes an imbalanced put of the
TPM ops and causes oopses on TIS based hardware.

This fix puts back the lost tpm_try_get_ops()

## References
- https://git.kernel.org/stable/c/bf84ef2dd2ccdcd8f2658476d34b51455f970ce4
- https://git.kernel.org/stable/c/39c8d760d44cb3fa0d67e8cd505df81cf4d80999
- https://git.kernel.org/stable/c/9d5171eab462a63e2fbebfccf6026e92be018f20
