# [H] scsi: ses: Handle enclosure with just a primary component gracefully

## Summary
Severity: High
Advisory: CVE-2023-53431
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-09-18
Source: https://osv.dev/vulnerability/CVE-2023-53431
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.25 <4.19.281, >=4.20.0 <5.4.241, >=5.5.0 <5.10.178, >=5.11.0 <5.15.108, >=5.16.0 <6.1.25, >=6.2.0 <6.2.12

## Details
In the Linux kernel, the following vulnerability has been resolved:

scsi: ses: Handle enclosure with just a primary component gracefully

This reverts commit 3fe97ff3d949 ("scsi: ses: Don't attach if enclosure
has no components") and introduces proper handling of case where there are
no detected secondary components, but primary component (enumerated in
num_enclosures) does exist. That fix was originally proposed by Ding Hui
<dinghui@sangfor.com.cn>.

Completely ignoring devices that have one primary enclosure and no
secondary one results in ses_intf_add() bailing completely

	scsi 2:0:0:254: enclosure has no enumerated components
        scsi 2:0:0:254: Failed to bind enclosure -12ven in valid configurations such

even on valid configurations with 1 primary and 0 secondary enclosures as
below:

	# sg_ses /dev/sg0
	  3PARdata  SES               3321
	Supported diagnostic pages:
	  Supported Diagnostic Pages [sdp] [0x0]
	  Configuration (SES) [cf] [0x1]
	  Short Enclosure Status (SES) [ses] [0x8]
	# sg_ses -p cf /dev/sg0
	  3PARdata  SES               3321
	Configuration diagnostic page:
	  number of secondary subenclosures: 0
	  generation code: 0x0
	  enclosure descriptor list
	    Subenclosure identifier: 0 [primary]
	      relative ES process id: 0, number of ES processes: 1
	      number of type descriptor headers: 1
	      enclosure logical identifier (hex): 20000002ac02068d
	      enclosure vendor: 3PARdata  product: VV                rev: 3321
	  type descriptor header and text list
	    Element type: Unspecified, subenclosure id: 0
	      number of possible elements: 1

The changelog for the original fix follows

=====
We can get a crash when disconnecting the iSCSI session,
the call trace like this:

  [ffff00002a00fb70] kfree at ffff00000830e224
  [ffff00002a00fba0] ses_intf_remove at ffff000001f200e4
  [ffff00002a00fbd0] device_del at ffff0000086b6a98
  [ffff00002a00fc50] device_unregister at ffff0000086b6d58
  [ffff00002a00fc70] __scsi_remove_device at ffff00000870608c
  [ffff00002a00fca0] scsi_remove_device at ffff000008706134
  [ffff00002a00fcc0] __scsi_remove_target at ffff0000087062e4
  [ffff00002a00fd10] scsi_remove_target at ffff0000087064c0
  [ffff00002a00fd70] __iscsi_unbind_session at ffff000001c872c4
  [ffff00002a00fdb0] process_one_work at ffff00000810f35c
  [ffff00002a00fe00] worker_thread at ffff00000810f648
  [ffff00002a00fe70] kthread at ffff000008116e98

In ses_intf_add, components count could be 0, and kcalloc 0 size scomp,
but not saved in edev->component[i].scratch

In this situation, edev->component[0].scratch is an invalid pointer,
when kfree it in ses_intf_remove_enclosure, a crash like above would happen
The call trace also could be other random cases when kfree cannot catch
the invalid pointer

We should not use edev->component[] array when the components count is 0
We also need check index when use edev->component[] array in
ses_enclosure_data_process
=====

## References
- https://git.kernel.org/stable/c/05143d90ac90b7abc6692285895a1ef460e008ee
- https://git.kernel.org/stable/c/110d425cdfb15006f3c4fde5264e786a247b6b36
- https://git.kernel.org/stable/c/176d7345b89ced72020a313bfa4e7f345d1c3aed
- https://git.kernel.org/stable/c/4e7c498c3713b09bef20c76c7319555637e8bbd5
- https://git.kernel.org/stable/c/c8e22b7a1694bb8d025ea636816472739d859145
- https://git.kernel.org/stable/c/eabc4872f172ecb8dd8536bc366a51868154a450
- https://git.kernel.org/stable/c/f8e702c54413eee2d8f94f61d18adadac7c87e87
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53431.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53431
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
