# [H] rnbd-srv: Zero the rsp buffer before using it

## Summary
Severity: High
Advisory: CVE-2026-43184
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-05-06
Source: https://osv.dev/vulnerability/CVE-2026-43184
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.8.0 <5.10.252, >=5.11.0 <5.15.202, >=5.16.0 <6.1.165, >=6.2.0 <6.6.128, >=6.7.0 <6.12.75, >=6.13.0 <6.18.16, >=6.19.0 <6.19.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

rnbd-srv: Zero the rsp buffer before using it

Before using the data buffer to send back the response message, zero it
completely. This prevents any stray bytes to be picked up by the client
side when there the message is exchanged between different protocol
versions.

## References
- https://git.kernel.org/stable/c/30868a6a5238849d554295aff3ce61d242d7fad8
- https://git.kernel.org/stable/c/69d26698e4fd44935510553809007151b2fe4db5
- https://git.kernel.org/stable/c/7aac0a30dcf41cdb510526740d9a2ab1520c5d98
- https://git.kernel.org/stable/c/852475278ca5e96e0c0275950e1a84203e602b33
- https://git.kernel.org/stable/c/b646e54d23b9b592d612a2036aab14e0f6c14206
- https://git.kernel.org/stable/c/c94ede3c436dfbd9cedd9cb69f604f6fc901b6a2
- https://git.kernel.org/stable/c/e2cacec7d4291300a282feb3af8eba57b93b15aa
- https://git.kernel.org/stable/c/e4272754063d52c9ad0169865add8816ba696471
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/43xxx/CVE-2026-43184.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-43184
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
