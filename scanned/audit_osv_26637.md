# [M] media: uvcvideo: Handle cameras with invalid descriptors

## Summary
Severity: Medium
Advisory: CVE-2023-53437
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-09-18
Source: https://osv.dev/vulnerability/CVE-2023-53437
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <4.14.308, >=4.15.0 <4.19.276, >=4.20.0 <5.4.235, >=5.5.0 <5.10.173, >=5.11.0 <5.15.100, >=5.12.0 <6.1.18, >=5.16.0 <6.2.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

media: uvcvideo: Handle cameras with invalid descriptors

If the source entity does not contain any pads, do not create a link.

## References
- https://git.kernel.org/stable/c/11196ee3916e50a5da3c1e6ecda19a02dca14ba3
- https://git.kernel.org/stable/c/1a76cfc388cf105d3e04ac592670a52a3864b1ba
- https://git.kernel.org/stable/c/2914259fcea23971c6fed8b2618d3a729a78c365
- https://git.kernel.org/stable/c/31a8d11d28b57656cebfbd4c0b8b76f6ad5b017d
- https://git.kernel.org/stable/c/41ddb251c68ac75c101d3a50a68c4629c9055e4c
- https://git.kernel.org/stable/c/4e4e6ca62e77539d4df8d13137e2683b10baddd9
- https://git.kernel.org/stable/c/c8f4a424af5879baefb0fb8a8a09b09ea1779483
- https://git.kernel.org/stable/c/d8aa2e1ae6426d7cbddf1735aed1a63ddf0e6909
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53437.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53437
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
