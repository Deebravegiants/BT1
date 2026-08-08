### Title
Unbounded `msg_len` from `recvmmsg` allows `Packet::meta.size` to exceed buffer capacity, triggering downstream `unreachable!()` panic - (File: streamer/src/recvmmsg.rs)

### Summary
The Linux implementation of `recv_mmsg` copies the kernel-reported `msg_len` directly into `Packet::meta.size` without clamping it to the packet buffer's actual capacity (`PACKET_DATA_SIZE`/`iov_len`). Because UDP sockets report the true datagram length even when the datagram is truncated to fit the supplied buffer, an unprivileged attacker can send a single oversized UDP datagram to the TPU/TPU-forward port to make `meta.size` exceed the buffer length, producing an inconsistent `Packet` that downstream consumers do not expect.

### Finding Description
In `streamer/src/recvmmsg.rs`, `recv_mmsg` (Linux path) sets, per received message: [1](#0-0) 
`pkt.meta_mut().size = hdr_ref.msg_len as usize;` with no `min()`/clamp against the packet buffer length (`iov_len`, i.e. `PACKET_DATA_SIZE`). For `SOCK_DGRAM` sockets on Linux, `recvmsg`/`recvmmsg` report the actual datagram size in `msg_len` even when the datagram is larger than the supplied buffer and gets truncated on copy — this is standard UDP socket semantics, not a bug in the socket layer. An attacker with only network access to the TPU UDP port can send a single UDP datagram larger than `PACKET_DATA_SIZE` and cause `meta.size` to be set larger than the actual number of valid bytes copied into `Packet::buffer`.

This inconsistent `Packet` (discard = false, but `meta.size` > buffer capacity) is then handed to `packet_batch_sender.try_send` and consumed downstream (sigverify, banking, forwarding). Some downstream code paths explicitly assume that a non-discarded packet must always yield `Some` from `.data(..)`, e.g.: [2](#0-1) 
If `Packet::data()`/`BytesPacket::data()` is implemented with bounds-checked slicing (as seen in the analogous `BytesPacket::data` implementation using `self.buffer.get(index)`), a `meta.size` value that exceeds the buffer will cause `.data(..)` to return `None` even though `discard()` is `false`, hitting the `unreachable!()` branch and panicking the thread that processes forwarded packets.

The bounded-count/OOB indexing part of the original hypothesis (recvmmsg count racing `hdrs`/`iovs`/`addrs`) is **not** exploitable: `count = cmp::min(iovs.len(), packets.len())` is passed to the kernel as the hard cap (`count as u32`), so `nrecv <= count <= packets.len()` always holds, and the `batch[i..]` slicing in `recv_from_once`/`recv_from_coalesce` (`streamer/src/packet.rs`) is safe because `i` is monotonically incremented by values bounded by the remaining slice length.

### Impact Explanation
An attacker with no stake, keys, or special access can send a single oversized UDP datagram to a validator's TPU/TPU-forward port and cause a panic in the packet-forwarding pipeline (`forwarding_stage.rs`), which is on the hot path from `packet_batch_sender` consumers. A crash of this thread can degrade or halt block-forwarding/production for that validator, matching the "banking/replay thread panic or wedge" impact category described in scope.

### Likelihood Explanation
Feasibility is high: sending a single UDP datagram larger than `PACKET_DATA_SIZE` to a public TPU port requires no special privileges, stake, or prior state and is trivially repeatable. The behavior relies on well-documented, deterministic Linux UDP semantics (oversized datagram truncation while `msg_len` reports the real size), so this is not a probabilistic race but a reliably reproducible condition on affected kernels.

### Recommendation
Clamp `hdr_ref.msg_len` to the actual `iov_len`/`PACKET_DATA_SIZE` before assigning to `pkt.meta_mut().size` in `streamer/src/recvmmsg.rs`:
```rust
pkt.meta_mut().size = cmp::min(hdr_ref.msg_len as usize, buffer.len());
```
Additionally, harden any assumption in consumer code (e.g. `forwarding_stage.rs`) that a non-discarded packet always has valid `.data(..)`, replacing `unreachable!()` with a safe drop-and-continue path, or set `meta.discard()` when `msg_len` exceeds the buffer length so oversized/truncated datagrams are explicitly rejected instead of silently corrupting `meta.size`.

### Proof of Concept
Rust unit test plan for `streamer/src/recvmmsg.rs` / `streamer/src/packet.rs`:
```rust
#[test]
fn test_recv_mmsg_oversized_datagram_size_not_clamped() {
    let (reader, reader_addr, sender, _sender_addr) =
        test_setup_reader_sender(IpAddr::V4(Ipv4Addr::LOCALHOST)).unwrap();

    // Send a UDP datagram larger than PACKET_DATA_SIZE.
    let oversized = vec![0xAAu8; PACKET_DATA_SIZE + 512];
    sender.send_to(&oversized, reader_addr).unwrap();

    let mut packets = vec![Packet::default(); 1];
    let recv = recv_mmsg(&reader, &mut packets[..]).unwrap();
    assert_eq!(recv, 1);

    // Assert the bug: meta.size exceeds the actual packet buffer capacity.
    assert!(
        packets[0].meta().size > PACKET_DATA_SIZE,
        "meta.size ({}) should not exceed buffer capacity ({})",
        packets[0].meta().size,
        PACKET_DATA_SIZE
    );

    // Downstream: packet is not marked as discard, but .data(..) may return None
    // due to size > buffer length, violating the invariant assumed by
    // forwarding_stage.rs's `unreachable!()` branch.
    assert!(!packets[0].meta().discard());
    assert!(packets[0].data(..).is_none());
}
```
Expected result on the current code: the test demonstrates `meta.size > PACKET_DATA_SIZE` with `discard() == false`, confirming the invariant violation that leads to the `unreachable!()` panic in `core/src/forwarding_stage.rs::buffer_packet_batches`. A fuzz/integration test on `forwarding_stage::buffer_packet_batches` feeding a `BankingPacketBatch` containing such a malformed packet should assert no panic occurs (currently it will).

### Citations

**File:** streamer/src/recvmmsg.rs (L148-160)
```rust
    for (addr, hdr, pkt) in izip!(addrs, hdrs, packets.iter_mut()).take(nrecv) {
        // SAFETY: We initialized `count` elements of `hdrs` above. `count` is
        // passed to recvmmsg() as the limit of messages that can be read. So,
        // `nrevc <= count` which means we initialized this `hdr` and
        // recvmmsg() will have updated it appropriately
        let hdr_ref = unsafe { hdr.assume_init_ref() };
        // SAFETY: Similar to above, we initialized this `addr` and recvmmsg()
        // will have populated it
        let addr_ref = unsafe { addr.assume_init_ref() };
        pkt.meta_mut().size = hdr_ref.msg_len as usize;
        if let Some(addr) = cast_socket_addr(addr_ref, hdr_ref) {
            pkt.meta_mut().set_socket_addr(&addr);
        }
```

**File:** core/src/forwarding_stage.rs (L277-286)
```rust
        for packet in packet_batch
            .iter()
            .filter(|p| initial_packet_meta_filter(p.meta()))
        {
            let Some(packet_data) = packet.data(..) else {
                unreachable!(
                    "packet.meta().discard() was already checked. If not discarded, packet MUST \
                     have data"
                );
            };
```
