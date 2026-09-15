# [H] netfilter: nf_tables: discard table flag update with pending basechain deletion

## Summary
Severity: High
Advisory: CVE-2024-35897
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-19
Source: https://osv.dev/vulnerability/CVE-2024-35897
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <5.4.274, >=5.5.0 <5.10.215, >=5.11.0 <5.15.155, >=5.13.0 <6.1.86, >=5.16.0 <6.6.26, >=6.2.0 <6.8.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

netfilter: nf_tables: discard table flag update with pending basechain deletion

Hook unregistration is deferred to the commit phase, same occurs with
hook updates triggered by the table dormant flag. When both commands are
combined, this results in deleting a basechain while leaving its hook
still registered in the core.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-265688.html
- https://git.kernel.org/stable/c/1bc83a019bbe268be3526406245ec28c2458a518
- https://git.kernel.org/stable/c/2aeb805a1bcd5f27c8c0d1a9d4d653f16d1506f4
- https://git.kernel.org/stable/c/6cbbe1ba76ee7e674a86abd43009b083a45838cb
- https://git.kernel.org/stable/c/7f609f630951b624348373cef99991ce08831927
- https://git.kernel.org/stable/c/9627fd0c6ea1c446741a33e67bc5709c59923827
- https://git.kernel.org/stable/c/9a3b90904d8a072287480eed4c3ece4b99d64f78
- https://git.kernel.org/stable/c/b58d0ac35f6d75ec1db8650a29dfd6f292c11362
- https://git.kernel.org/stable/c/e75faf01e22ec7dc671640fa0e0968964fafd2fc
- https://lists.debian.org/debian-lts-announce/2024/06/msg00017.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/35xxx/CVE-2024-35897.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-35897
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
