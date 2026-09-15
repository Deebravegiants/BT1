# [H] net: usb: Remove disruptive netif_wake_queue in rtl8150_set_multicast

## Summary
Severity: High
Advisory: CVE-2025-40140
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-11-12
Source: https://osv.dev/vulnerability/CVE-2025-40140
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.12 <5.4.301, >=5.5.0 <5.10.246, >=5.11.0 <5.15.195, >=5.16.0 <6.1.156, >=6.2.0 <6.6.112, >=6.7.0 <6.12.53, >=6.13.0 <6.17.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: usb: Remove disruptive netif_wake_queue in rtl8150_set_multicast

syzbot reported WARNING in rtl8150_start_xmit/usb_submit_urb.
This is the sequence of events that leads to the warning:

rtl8150_start_xmit() {
	netif_stop_queue();
	usb_submit_urb(dev->tx_urb);
}

rtl8150_set_multicast() {
	netif_stop_queue();
	netif_wake_queue();		<-- wakes up TX queue before URB is done
}

rtl8150_start_xmit() {
	netif_stop_queue();
	usb_submit_urb(dev->tx_urb);	<-- double submission
}

rtl8150_set_multicast being the ndo_set_rx_mode callback should not be
calling netif_stop_queue and notif_start_queue as these handle
TX queue synchronization.

The net core function dev_set_rx_mode handles the synchronization
for rtl8150_set_multicast making it safe to remove these locks.

## References
- https://git.kernel.org/stable/c/114e05344763a102a8844efd96ec06ba99293ccd
- https://git.kernel.org/stable/c/1a08a37ac03d07a1608a1592791041cac979fbc3
- https://git.kernel.org/stable/c/54f8ef1a970a8376e5846ed90854decf7c00555d
- https://git.kernel.org/stable/c/6053e47bbf212b93c051beb4261d7d5a409d0ce3
- https://git.kernel.org/stable/c/6394bade9daab8e318c165fe43bba012bf13cd8e
- https://git.kernel.org/stable/c/958baf5eaee394e5fd976979b0791a875f14a179
- https://git.kernel.org/stable/c/9d72df7f5eac946f853bf49c428c4e87a17d91da
- https://git.kernel.org/stable/c/cce3c0e21cdd15bcba5c35d3af1700186de8f187
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/40xxx/CVE-2025-40140.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-40140
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
