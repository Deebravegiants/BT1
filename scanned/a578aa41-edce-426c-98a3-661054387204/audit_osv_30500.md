# [H] virtio_net: Add hash_key_length check

## Summary
Severity: High
Advisory: CVE-2024-53082
Ecosystem: Linux
CVSS: 8.4 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-11-19
Source: https://osv.dev/vulnerability/CVE-2024-53082
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.18.0 <6.1.117, >=6.2.0 <6.6.61, >=6.7.0 <6.11.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

virtio_net: Add hash_key_length check

Add hash_key_length check in virtnet_probe() to avoid possible out of
bound errors when setting/reading the hash key.

## References
- https://git.kernel.org/stable/c/3f7d9c1964fcd16d02a8a9d4fd6f6cb60c4cc530
- https://git.kernel.org/stable/c/6a18a783b1fa590ad1ed785907263e4b86adcfe2
- https://git.kernel.org/stable/c/af0aa8aecbe8985079232902894cc4cb62795691
- https://git.kernel.org/stable/c/f3401e3c8d339ddb6ccb2e3d11ad634b7846a806
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/53xxx/CVE-2024-53082.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-53082
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
