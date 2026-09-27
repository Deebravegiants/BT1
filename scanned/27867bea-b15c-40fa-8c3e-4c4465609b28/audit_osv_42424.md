# [C] mctp: serial: handle zero-length frames to prevent rx buffer overflow

## Summary
Severity: Critical
Advisory: CVE-2026-68124
Ecosystem: Linux
CVSS: 9.6 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-68124
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.17.0 <6.1.183, >=6.2.0 <6.6.148, >=6.7.0 <6.12.101, >=6.13.0 <6.18.42, >=6.19.0 <7.1.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

mctp: serial: handle zero-length frames to prevent rx buffer overflow

The MCTP serial receive state machine reads a frame length byte in
mctp_serial_push_header() case 2 and validates it upper-bound-only:

	if (c > MCTP_SERIAL_FRAME_MTU) {
		dev->rxstate = STATE_ERR;
	} else {
		dev->rxlen = c;
		dev->rxpos = 0;
		dev->rxstate = STATE_DATA;
		...
	}

A length of zero passes this check, so rxlen is set to 0 and the state
machine advances to STATE_DATA. In mctp_serial_push() STATE_DATA, the
incoming byte is stored and rxpos incremented before the terminator is

	dev->rxbuf[dev->rxpos] = c;
	dev->rxpos++;
	dev->rxstate = STATE_DATA;
	if (dev->rxpos == dev->rxlen) {
		dev->rxpos = 0;
		dev->rxstate = STATE_TRAILER;
	}

With rxlen == 0 the "rxpos == rxlen" terminator can never fire (rxpos is
already 1 on the first data byte), so subsequent bytes are written past
the end of the fixed 74-byte rxbuf, which is the last member of the
netdev private area. Every following data byte is an attacker-controlled
1-byte out-of-bounds heap write, and the overflow continues until a
frame (0x7e) or escape byte resets the parser -- effectively unbounded.

Reaching this requires CAP_NET_ADMIN to attach the N_MCTP line
discipline and bring the resulting mctpserialN netdev up, after which
the bytes arrive via the tty receive path.

Route a zero-length frame straight to STATE_TRAILER instead of
STATE_DATA. The trailer/framing bytes are still consumed, and the frame
resolves to a zero-length skb that the MCTP core rejects; the parser
never enters STATE_DATA with rxlen == 0, so the out-of-bounds write can
no longer occur.

KASAN, on a frame of 0x7e 0x01 0x00 followed by data bytes (before this
change):

  UBSAN: array-index-out-of-bounds in drivers/net/mctp/mctp-serial.c:370
  index 74 is out of range for type 'u8 [74]'
  BUG: KASAN: slab-out-of-bounds in mctp_serial_tty_receive_buf
  Write of size 1 at addr ... by task kworker/u16:0
   mctp_serial_tty_receive_buf
   tty_ldisc_receive_buf
   flush_to_ldisc
  Allocated by task 152:
   alloc_netdev_mqs
   mctp_serial_open

v2: route zero-length frames to STATE_TRAILER instead of STATE_ERR so
    the trailer/framing bytes are still consumed (Jeremy Kerr).

Found by 0sec automated security-research tooling (https://0sec.ai).

## References
- https://git.kernel.org/stable/c/06a6b606129c8a25cd457760f5370f3ff01fe05d
- https://git.kernel.org/stable/c/36dc6d6964a3b90411cc7944cd9b8b6f67b9807b
- https://git.kernel.org/stable/c/64b96ae7912244d55257aa330d9569ee0a8f8d99
- https://git.kernel.org/stable/c/68819427bc07eca7963a9e8be19e5272cc29186c
- https://git.kernel.org/stable/c/793b9b729f1e8de57be8c8daf1a9838be96cabed
- https://git.kernel.org/stable/c/f80ba170d7b3a44e3d244a2c8e06031d61bf3b23
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68124.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-68124
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
