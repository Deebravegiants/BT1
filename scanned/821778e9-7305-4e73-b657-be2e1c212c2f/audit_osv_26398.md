# [H] netfilter: nft_payload: incorrect arithmetics when fetching VLAN header bits

## Summary
Severity: High
Advisory: CVE-2023-53033
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-03-27
Source: https://osv.dev/vulnerability/CVE-2023-53033
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.5.0 <5.10.164, >=5.11.0 <5.15.89, >=5.16.0 <6.1.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

netfilter: nft_payload: incorrect arithmetics when fetching VLAN header bits

If the offset + length goes over the ethernet + vlan header, then the
length is adjusted to copy the bytes that are within the boundaries of
the vlan_ethhdr scratchpad area. The remaining bytes beyond ethernet +
vlan header are copied directly from the skbuff data area.

Fix incorrect arithmetic operator: subtract, not add, the size of the
vlan header in case of double-tagged packets to adjust the length
accordingly to address CVE-2023-0179.

## References
- https://git.kernel.org/stable/c/550efeff989b041f3746118c0ddd863c39ddc1aa
- https://git.kernel.org/stable/c/696e1a48b1a1b01edad542a1ef293665864a4dd0
- https://git.kernel.org/stable/c/76ef74d4a379faa451003621a84e3498044e7aa3
- https://git.kernel.org/stable/c/a8acfe2c6fb99f9375a9325807a179cd8c32e6e3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53033.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53033
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
