# [H] wifi: iwlwifi: mvm: clean up ROC on failure

## Summary
Severity: High
Advisory: CVE-2025-21906
Ecosystem: Linux
CVSS: 7.6 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:H)
Published: 2025-04-01
Source: https://osv.dev/vulnerability/CVE-2025-21906
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.9.0 <6.12.19, >=6.13.0 <6.13.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

wifi: iwlwifi: mvm: clean up ROC on failure

If the firmware fails to start the session protection, then we
do call iwl_mvm_roc_finished() here, but that won't do anything
at all because IWL_MVM_STATUS_ROC_P2P_RUNNING was never set.
Set IWL_MVM_STATUS_ROC_P2P_RUNNING in the failure/stop path.
If it started successfully before, it's already set, so that
doesn't matter, and if it didn't start it needs to be set to
clean up.

Not doing so will lead to a WARN_ON() later on a fresh remain-
on-channel, since the link is already active when activated as
it was never deactivated.

## References
- https://git.kernel.org/stable/c/a88c18409b5d69f426d5acc583c053eac71756a3
- https://git.kernel.org/stable/c/d1a12fcb9051bbf38b2e5af310ffb102a0fab6f9
- https://git.kernel.org/stable/c/f9751163bffd3fe60794929829f810968c6de73d
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/21xxx/CVE-2025-21906.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-21906
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
