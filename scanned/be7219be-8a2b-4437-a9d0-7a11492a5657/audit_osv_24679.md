# [M] Usage of Uninitialized Timer during forwarding of Fragments with SFR

## Summary
Severity: Medium
Advisory: CVE-2023-24826
Aliases: GHSA-xfj4-9g7w-f4gh
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-05-30
Source: https://osv.dev/vulnerability/CVE-2023-24826
Type: osv

## Details
RIOT-OS, an operating system for Internet of Things (IoT) devices, contains a network stack with the ability to process 6LoWPAN frames. Prior to version 2023.04, an attacker can send crafted frames to the device to trigger the usage of an uninitialized object leading to denial of service. This issue is fixed in version 2023.04. As a workaround, disable fragment forwarding or SFR.

## References
- https://github.com/RIOT-OS/RIOT/blob/ccbb304eae7b59e8aca24a6ffd095b5b3f7720ee/sys/net/gnrc/network_layer/sixlowpan/frag/sfr/gnrc_sixlowpan_frag_sfr.c#L402
- https://github.com/RIOT-OS/RIOT/blob/ccbb304eae7b59e8aca24a6ffd095b5b3f7720ee/sys/net/gnrc/network_layer/sixlowpan/frag/sfr/gnrc_sixlowpan_frag_sfr.c#L420
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/24xxx/CVE-2023-24826.json
- https://github.com/RIOT-OS/RIOT/security/advisories/GHSA-xfj4-9g7w-f4gh
- https://nvd.nist.gov/vuln/detail/CVE-2023-24826
- https://github.com/RIOT-OS/RIOT/commit/287f030af20e829469cdf740606148018a5a220d
