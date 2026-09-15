# [C] NFSD: Fix ia_size underflow

## Summary
Severity: Critical
Advisory: CVE-2022-48828
Ecosystem: Linux
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:H)
Published: 2024-07-16
Source: https://osv.dev/vulnerability/CVE-2022-48828
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.12 <5.4.295, >=5.5.0 <5.10.220, >=5.11.0 <5.15.24, >=5.16.0 <5.16.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

NFSD: Fix ia_size underflow

iattr::ia_size is a loff_t, which is a signed 64-bit type. NFSv3 and
NFSv4 both define file size as an unsigned 64-bit type. Thus there
is a range of valid file size values an NFS client can send that is
already larger than Linux can handle.

Currently decode_fattr4() dumps a full u64 value into ia_size. If
that value happens to be larger than S64_MAX, then ia_size
underflows. I'm about to fix up the NFSv3 behavior as well, so let's
catch the underflow in the common code path: nfsd_setattr().

## References
- https://cert-portal.siemens.com/productcert/html/ssa-265688.html
- https://cert-portal.siemens.com/productcert/html/ssa-355557.html
- https://git.kernel.org/stable/c/38d02ba22e43b6fc7d291cf724bc6e3b7be6626b
- https://git.kernel.org/stable/c/8e0ecaf7a7e57b30284d6b3289cc436100fadc48
- https://git.kernel.org/stable/c/d2211e6e34d0755f35e2f8c22d81999fa81cfc71
- https://git.kernel.org/stable/c/da22ca1ad548429d7822011c54cfe210718e0aa7
- https://git.kernel.org/stable/c/e6faac3f58c7c4176b66f63def17a34232a17b0e
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/48xxx/CVE-2022-48828.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-48828
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
