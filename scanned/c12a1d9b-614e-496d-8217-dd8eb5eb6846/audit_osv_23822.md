# [H] scsi: lpfc: Fix null pointer dereference after failing to issue FLOGI and PLOGI

## Summary
Severity: High
Advisory: CVE-2022-49535
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49535
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.11.0 <5.15.181, >=5.16.0 <5.18.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

scsi: lpfc: Fix null pointer dereference after failing to issue FLOGI and PLOGI

If lpfc_issue_els_flogi() fails and returns non-zero status, the node
reference count is decremented to trigger the release of the nodelist
structure. However, if there is a prior registration or dev-loss-evt work
pending, the node may be released prematurely.  When dev-loss-evt
completes, the released node is referenced causing a use-after-free null
pointer dereference.

Similarly, when processing non-zero ELS PLOGI completion status in
lpfc_cmpl_els_plogi(), the ndlp flags are checked for a transport
registration before triggering node removal.  If dev-loss-evt work is
pending, the node may be released prematurely and a subsequent call to
lpfc_dev_loss_tmo_handler() results in a use after free ndlp dereference.

Add test for pending dev-loss before decrementing the node reference count
for FLOGI, PLOGI, PRLI, and ADISC handling.

## References
- https://git.kernel.org/stable/c/10663ebec0ad5c78493a0dd34c9ee4d73d7ca0df
- https://git.kernel.org/stable/c/577a942df3de2666f6947bdd3a5c9e8d30073424
- https://git.kernel.org/stable/c/c7dc74ab7975c9b96284abfe4cca756d75fa4604
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49535.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49535
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
