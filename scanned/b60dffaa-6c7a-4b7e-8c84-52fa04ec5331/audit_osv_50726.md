# [M] CVE-2020-35513

## Summary
Severity: Medium
Advisory: CVE-2020-35513
CVSS: 4.9 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-01-26
Source: https://osv.dev/vulnerability/CVE-2020-35513
Type: osv

## Details
A flaw incorrect umask during file or directory modification in the Linux kernel NFS (network file system) functionality was found in the way user create and delete object using NFSv4.2 or newer if both simultaneously accessing the NFS by the other process that is not using new NFSv4.2. A user with access to the NFS could use this flaw to starve the resources causing denial of service.

## References
- https://patchwork.kernel.org/project/linux-nfs/patch/20180403203916.GH20297%40fieldses.org/
- https://bugzilla.redhat.com/show_bug.cgi?id=1911309
