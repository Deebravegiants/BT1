# [H] CVE-2021-47198

## Summary
Severity: High
Advisory: CVE-2021-47198
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-04-10
Source: https://osv.dev/vulnerability/CVE-2021-47198
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

scsi: lpfc: Fix use-after-free in lpfc_unreg_rpi() routine

An error is detected with the following report when unloading the driver:
  "KASAN: use-after-free in lpfc_unreg_rpi+0x1b1b"

The NLP_REG_LOGIN_SEND nlp_flag is set in lpfc_reg_fab_ctrl_node(), but the
flag is not cleared upon completion of the login.

This allows a second call to lpfc_unreg_rpi() to proceed with nlp_rpi set
to LPFC_RPI_ALLOW_ERROR.  This results in a use after free access when used
as an rpi_ids array index.

Fix by clearing the NLP_REG_LOGIN_SEND nlp_flag in
lpfc_mbx_cmpl_fc_reg_login().

## References
- https://git.kernel.org/stable/c/79b20beccea3a3938a8500acef4e6b9d7c66142f
- https://git.kernel.org/stable/c/dbebf865b3239595c1d4dba063b122862583b52a
