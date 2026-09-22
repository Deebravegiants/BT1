# [H] TOCTOU double copyin in illumos dld ioctl handling causes kernel heap corruption

## Summary
Severity: High
Advisory: CVE-2026-15449
CVSS: 7.5 (CVSS:4.0/AV:L/AC:L/AT:P/PR:L/UI:N/VC:N/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-07-16
Source: https://osv.dev/vulnerability/CVE-2026-15449
Type: osv

## Details
A time-of-check to time-of-use (TOCTOU) flaw in the illumos data-link pseudo-driver (dld) affects handling of the DLDIOC_GETMACPROP and DLDIOC_SETMACPROP ioctls on /dev/dld. drv_ioc_prop_common() in usr/src/uts/common/io/dld/dld_drv.c copies the dld_ioc_macprop_t ioctl header in once to read its pr_valsize field, sizes and allocates a kernel heap buffer from that value, and then copies the full request in a second time from the same unprivileged user address. A concurrent thread can enlarge pr_valsize between the two copyins, so the second copyin and the subsequent property handling write beyond the end of the undersized allocation and corrupt the kernel heap. An unprivileged local user, including one confined to a non-global zone that owns a datalink, can trigger this to panic the system. The resulting kernel heap corruption may be usable for further compromise.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/15xxx/CVE-2026-15449.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-15449
- https://illumos.org/issues/18020
- https://github.com/illumos/illumos-gate/commit/6959feb5b430411a4809b06c53dcdb42fb525eac
- https://github.com/illumos/illumos-gate
- https://illumos.topicbox.com/groups/developer/T923147fae854a738-M03c29e1be33dac2a5e3d9535/18020-double-copyin-of-dldioc-consumers
