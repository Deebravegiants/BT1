# [H] ubi: ubi_wl_put_peb: Fix infinite loop when wear-leveling work failed

## Summary
Severity: High
Advisory: CVE-2023-53481
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-10-01
Source: https://osv.dev/vulnerability/CVE-2023-53481
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.25 <4.14.308, >=4.15.0 <4.19.276, >=4.20.0 <5.4.235, >=5.5.0 <5.10.173, >=5.11.0 <5.15.100, >=5.16.0 <6.1.18, >=6.2.0 <6.2.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

ubi: ubi_wl_put_peb: Fix infinite loop when wear-leveling work failed

Following process will trigger an infinite loop in ubi_wl_put_peb():

	ubifs_bgt		ubi_bgt
ubifs_leb_unmap
  ubi_leb_unmap
    ubi_eba_unmap_leb
      ubi_wl_put_peb	wear_leveling_worker
                          e1 = rb_entry(rb_first(&ubi->used)
			  e2 = get_peb_for_wl(ubi)
			  ubi_io_read_vid_hdr  // return err (flash fault)
			  out_error:
			    ubi->move_from = ubi->move_to = NULL
			    wl_entry_destroy(ubi, e1)
			      ubi->lookuptbl[e->pnum] = NULL
      retry:
        e = ubi->lookuptbl[pnum];	// return NULL
	if (e == ubi->move_from) {	// NULL == NULL gets true
	  goto retry;			// infinite loop !!!

$ top
  PID USER      PR  NI    VIRT    RES    SHR S  %CPU %MEM     COMMAND
  7676 root     20   0       0      0      0 R 100.0  0.0  ubifs_bgt0_0

Fix it by:
 1) Letting ubi_wl_put_peb() returns directly if wearl leveling entry has
    been removed from 'ubi->lookuptbl'.
 2) Using 'ubi->wl_lock' protecting wl entry deletion to preventing an
    use-after-free problem for wl entry in ubi_wl_put_peb().

Fetch a reproducer in [Link].

## References
- https://git.kernel.org/stable/c/3afaaf6f5867dc4ad383808d4053f428ec7b867d
- https://git.kernel.org/stable/c/4d57a7333e26040f2b583983e1970d9d460e56b0
- https://git.kernel.org/stable/c/5af1c643184a5d09ff5b3f334077a4d0a163c677
- https://git.kernel.org/stable/c/8a18856e074479bd050b01e688c58defadce7ab0
- https://git.kernel.org/stable/c/b40d2fbf47af58377e898b5062077a47bb28a132
- https://git.kernel.org/stable/c/b5be23f6ae610bdb262160a1f294afee6d0e6a69
- https://git.kernel.org/stable/c/cc4bc532acda66189bddc03b3fe1ad689d9a48a2
- https://git.kernel.org/stable/c/f006f596fe851c3b6aae60b79f89f89f0e515d2f
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53481.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53481
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
