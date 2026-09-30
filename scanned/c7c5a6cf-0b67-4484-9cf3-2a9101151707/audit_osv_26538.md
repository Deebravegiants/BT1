# [H] scsi: qla2xxx: Wait for io return on terminate rport

## Summary
Severity: High
Advisory: CVE-2023-53322
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-09-16
Source: https://osv.dev/vulnerability/CVE-2023-53322
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.34 <4.14.322, >=4.15.0 <4.19.291, >=4.20.0 <5.4.251, >=5.5.0 <5.10.188, >=5.11.0 <5.15.121, >=5.16.0 <6.1.40, >=6.2.0 <6.4.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

scsi: qla2xxx: Wait for io return on terminate rport

System crash due to use after free.
Current code allows terminate_rport_io to exit before making
sure all IOs has returned. For FCP-2 device, IO's can hang
on in HW because driver has not tear down the session in FW at
first sign of cable pull. When dev_loss_tmo timer pops,
terminate_rport_io is called and upper layer is about to
free various resources. Terminate_rport_io trigger qla to do
the final cleanup, but the cleanup might not be fast enough where it
leave qla still holding on to the same resource.

Wait for IO's to return to upper layer before resources are freed.

## References
- https://git.kernel.org/stable/c/079c8264ed9fea8cbcac01ad29040f901cbc3692
- https://git.kernel.org/stable/c/4647d2e88918a078359d1532d90c417a38542c9e
- https://git.kernel.org/stable/c/5bcdaafd92be6035ddc77fa76650cf9dd5b864c4
- https://git.kernel.org/stable/c/8a55556cd7e0220486163b1285ce11a8be2ce5fa
- https://git.kernel.org/stable/c/90770dad1eb30967ebd8d37d82830bcf270b3293
- https://git.kernel.org/stable/c/a9fe97fb7b4ee21bffb76f2acb05769bad27ae70
- https://git.kernel.org/stable/c/d25fded78d88e1515439b3ba581684d683e0b6ab
- https://git.kernel.org/stable/c/fc0cba0c7be8261a1625098bd1d695077ec621c9
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53322.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53322
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
