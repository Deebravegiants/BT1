# [H] ibmvnic: Add tx check to prevent skb leak

## Summary
Severity: High
Advisory: CVE-2024-41066
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-07-29
Source: https://osv.dev/vulnerability/CVE-2024-41066
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.14.0 <6.1.101, >=6.2.0 <6.6.42, >=6.7.0 <6.9.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

ibmvnic: Add tx check to prevent skb leak

Below is a summary of how the driver stores a reference to an skb during
transmit:
    tx_buff[free_map[consumer_index]]->skb = new_skb;
    free_map[consumer_index] = IBMVNIC_INVALID_MAP;
    consumer_index ++;
Where variable data looks like this:
    free_map == [4, IBMVNIC_INVALID_MAP, IBMVNIC_INVALID_MAP, 0, 3]
                                               	consumer_index^
    tx_buff == [skb=null, skb=<ptr>, skb=<ptr>, skb=null, skb=null]

The driver has checks to ensure that free_map[consumer_index] pointed to
a valid index but there was no check to ensure that this index pointed
to an unused/null skb address. So, if, by some chance, our free_map and
tx_buff lists become out of sync then we were previously risking an
skb memory leak. This could then cause tcp congestion control to stop
sending packets, eventually leading to ETIMEDOUT.

Therefore, add a conditional to ensure that the skb address is null. If
not then warn the user (because this is still a bug that should be
patched) and free the old pointer to prevent memleak/tcp problems.

## References
- https://git.kernel.org/stable/c/0983d288caf984de0202c66641577b739caad561
- https://git.kernel.org/stable/c/16ad1557cae582e79bb82dddd612d9bdfaa11d4c
- https://git.kernel.org/stable/c/267c61c4afed0ff9a2e83462abad3f41d8ca1f06
- https://git.kernel.org/stable/c/e7b75def33eae61ddaad6cb616c517dc3882eb2a
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/41xxx/CVE-2024-41066.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-41066
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
