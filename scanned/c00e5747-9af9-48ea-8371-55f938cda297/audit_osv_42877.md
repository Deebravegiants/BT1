# [C] scsi: xen: scsiback: Free unsubmitted command instead of double-putting it

## Summary
Severity: Critical
Advisory: CVE-2026-72085
Ecosystem: Linux
CVSS: 9.3 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72085
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.6.0 <5.15.212, >=5.16.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

scsi: xen: scsiback: Free unsubmitted command instead of double-putting it

scsiback_get_pend_req() obtains a command tag and returns a vscsibk_pend
whose embedded se_cmd has only been memset to 0, so its cmd_kref is 0;
the se_cmd is initialised (kref_init() via target_init_cmd()) only
later, in scsiback_cmd_exec(), on the successful VSCSIIF_ACT_SCSI_CDB
path. The two error paths in scsiback_do_cmd_fn() taken before the
command is submitted -- a failed scsiback_gnttab_data_map() and an
unknown ring_req.act -- call
transport_generic_free_cmd(&pending_req->se_cmd, 0), which kref_put()s a
refcount of 0. That underflows it ("refcount_t: underflow;
use-after-free") and, as the release function is not run, leaks the
command tag.

Impact: a pvSCSI guest can leak every command tag of a LUN's session,
stopping the LUN, by submitting requests with a bad grant reference or
an unknown request type; under panic_on_warn the refcount underflow
panics the host.

Add a helper that just returns the tag with target_free_tag() and sends
the error response. It frees the tag while the v2p reference still pins
the session, and snapshots the response fields beforehand because
freeing the tag can let another ring reuse the pending_req slot.

## References
- https://git.kernel.org/stable/c/1e97c404e44991fb087c38ccd7414f2d326f9b74
- https://git.kernel.org/stable/c/9c0f6894982b1f13bda220707497b25ac9c95bdb
- https://git.kernel.org/stable/c/a13b789497a7fdd27d4d63f5c69d23db706ef0fe
- https://git.kernel.org/stable/c/ca978f8a93d4d36841839bf2847d29b88c2591d6
- https://git.kernel.org/stable/c/f1516c56ac540da1769f264c3cfefe4499548a5d
- https://git.kernel.org/stable/c/fa588f28401102652068c4cc75e135507f4b5106
- https://git.kernel.org/stable/c/fcd64d4d97af5d9736f31040f8ed8cd4c17e4c45
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72085.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72085
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
