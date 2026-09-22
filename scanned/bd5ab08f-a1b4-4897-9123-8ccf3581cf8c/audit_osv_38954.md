# [H] net: usb: kaweth: remove TX queue manipulation in kaweth_set_rx_mode

## Summary
Severity: High
Advisory: CVE-2026-43180
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-06
Source: https://osv.dev/vulnerability/CVE-2026-43180
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.12 <5.10.252, >=5.11.0 <5.15.202, >=5.16.0 <6.1.165, >=6.2.0 <6.6.128, >=6.7.0 <6.12.75, >=6.13.0 <6.18.16, >=6.19.0 <6.19.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: usb: kaweth: remove TX queue manipulation in kaweth_set_rx_mode

kaweth_set_rx_mode(), the ndo_set_rx_mode callback, calls
netif_stop_queue() and netif_wake_queue(). These are TX queue flow
control functions unrelated to RX multicast configuration.

The premature netif_wake_queue() can re-enable TX while tx_urb is still
in-flight, leading to a double usb_submit_urb() on the same URB:

kaweth_start_xmit() {
    netif_stop_queue();
    usb_submit_urb(kaweth->tx_urb);
}

kaweth_set_rx_mode() {
    netif_stop_queue();
    netif_wake_queue();             // wakes TX queue before URB is done
}

kaweth_start_xmit() {
    netif_stop_queue();
    usb_submit_urb(kaweth->tx_urb); // URB submitted while active
}

This triggers the WARN in usb_submit_urb():

  "URB submitted while active"

This is a similar class of bug fixed in rtl8150 by

- commit 958baf5eaee3 ("net: usb: Remove disruptive netif_wake_queue in rtl8150_set_multicast").

Also kaweth_set_rx_mode() is already functionally broken, the
real set_rx_mode action is performed by kaweth_async_set_rx_mode(),
which in turn is not a no-op only at ndo_open() time.

## References
- https://git.kernel.org/stable/c/443a830b1dc4f85c7560da59d4494b629feee215
- https://git.kernel.org/stable/c/586318c2730433184c6f1d21183e346ddf25e81d
- https://git.kernel.org/stable/c/64868f5ecadeb359a49bc4485bfa7c497047f13a
- https://git.kernel.org/stable/c/8367c0e90126426e60581e4c07e1ec4411a0f843
- https://git.kernel.org/stable/c/9c79b839a63980c7da7ec5db895198045e154112
- https://git.kernel.org/stable/c/a2cd4b4db315a845a5603d08c9d03b11ddfc799d
- https://git.kernel.org/stable/c/ef9b10a020503888eb6c8ed85a3d901a624ede4c
- https://git.kernel.org/stable/c/fc393af769af845d9985e2845e49553d8f015a64
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/43xxx/CVE-2026-43180.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-43180
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
