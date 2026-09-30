# [M] CVE-2020-36789

## Summary
Severity: Medium
Advisory: CVE-2020-36789
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-04-17
Source: https://osv.dev/vulnerability/CVE-2020-36789
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

can: dev: can_get_echo_skb(): prevent call to kfree_skb() in hard IRQ context

If a driver calls can_get_echo_skb() during a hardware IRQ (which is often, but
not always, the case), the 'WARN_ON(in_irq)' in
net/core/skbuff.c#skb_release_head_state() might be triggered, under network
congestion circumstances, together with the potential risk of a NULL pointer
dereference.

The root cause of this issue is the call to kfree_skb() instead of
dev_kfree_skb_irq() in net/core/dev.c#enqueue_to_backlog().

This patch prevents the skb to be freed within the call to netif_rx() by
incrementing its reference count with skb_get(). The skb is finally freed by
one of the in-irq-context safe functions: dev_consume_skb_any() or
dev_kfree_skb_any(). The "any" version is used because some drivers might call
can_get_echo_skb() in a normal context.

The reason for this issue to occur is that initially, in the core network
stack, loopback skb were not supposed to be received in hardware IRQ context.
The CAN stack is an exeption.

This bug was previously reported back in 2017 in [1] but the proposed patch
never got accepted.

While [1] directly modifies net/core/dev.c, we try to propose here a
smoother modification local to CAN network stack (the assumption
behind is that only CAN devices are affected by this issue).

[1] http://lore.kernel.org/r/57a3ffb6-3309-3ad5-5a34-e93c3fe3614d@cetitec.com

## References
- https://git.kernel.org/stable/c/ab46748bf98864f9c3f5559060bf8caf9df2b41e
- https://git.kernel.org/stable/c/2283f79b22684d2812e5c76fc2280aae00390365
- https://git.kernel.org/stable/c/248b71ce92d4f3a574b2537f9838f48e892618f4
- https://git.kernel.org/stable/c/3a922a85701939624484e7f2fd07d32beed00d25
- https://git.kernel.org/stable/c/451187b20431924d13fcfecc500d7cd2d9951bac
- https://git.kernel.org/stable/c/7e4cf2ec0ca236c3e5f904239cec6efe1f3baf22
- https://git.kernel.org/stable/c/87530b557affe01c764de32dbeb58cdf47234574
