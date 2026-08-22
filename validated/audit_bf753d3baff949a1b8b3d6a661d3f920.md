### Title
Unvalidated cross-process rkyv deserialization in `agentwire` shared-memory IPC allows a compromised sandboxed agent to corrupt the trusted broker process - (File: `agentwire/src/port.rs`)

### Summary
`agentwire`'s shared-memory `Port` implementation trusts a length field and archive contents coming from the *other* side of the IPC channel without any structural validation before treating the bytes as a live `rkyv` archive. This is the same bug class as the Firedancer report: a producer that is a separate, potentially compromised process writes a length/offset-bearing structure into shared memory, and the consumer trusts those embedded fields to index and interpret memory rather than validating them first.

### Finding Description
Every `SharedPort` agent (e.g. `qr_code::Agent`, the Python ML mega-agents, camera/thermal agents) runs in its own OS process, spawned via `Process::spawn_process`, and is deliberately put in a reduced-privilege sandbox (`unshare(CLONE_NEWUSER | CLONE_NEWIPC[...])` in `sandbox_agent`). [1](#0-0) 

Communication between the trusted broker process and the sandboxed agent process happens over a shared-memory ring implemented in `agentwire/src/port.rs`. Messages are framed by a `usize` length prefix followed by an `rkyv` archive, and are read back with:
```rust
unsafe fn deserialize_message<T>(buf: &[u8]) -> &T::Archived {
    let size = usize::from_ne_bytes(buf[..mem::size_of::<usize>()].try_into().unwrap());
    let bytes = &buf[mem::size_of::<usize>()..mem::size_of::<usize>() + size];
    unsafe { rkyv::archived_root::<T>(bytes) }
}
``` [2](#0-1) 

This mirrors `fd_store`'s `during_frag`/`after_frag`, where a size/offset field originating from another process (`fd_shred34_t.shred_sz`/`offset`) is copied and then trusted to index into memory before any structural check. Here, `size` is read directly from attacker-influenced shared memory and used to slice `buf`, and the resulting bytes are handed to `rkyv::archived_root`, which is the *unchecked* rkyv API — it does not run `bytecheck` validation of internal relative pointers/lengths (the crate is not used with the `validation`/`check_archived_root` path anywhere in the codebase, confirmed by the absence of `check_archived_root`/`bytecheck` usage in `port.rs`). If the archive's internal `RelPtr`s (used by `ArchivedString`, `ArchivedVec`, etc.) are corrupted, subsequent field access on the "trusted" side can read out-of-bounds memory in the trusted process.

The reachable attack surface: the `qr-code` agent process decodes attacker-fully-controlled QR/MECARD-like image data with the `rxing` library and only produces a `String` `payload`/`Points`, but it runs in the sandbox and any memory-safety bug in `rxing` (parsing hostile QR bitstreams) that yields arbitrary/attacker-influenced bytes written into `port.output()` shared memory would be deserialized without validation by the broker process via `spawn_shared_tx_task`, which calls `deserialize_message::<T::Output>` on the *output* buffer and then `archived.deserialize(...)`. [3](#0-2) [4](#0-3) 

This is a genuine architectural analog of the reported bug class ("agent-IPC trust boundaries"): a sandboxed, externally-reachable-input-handling process (`qr-code`) is trusted by the parent broker to send well-formed serialized data, and the deserialization path has no defense-in-depth validation of the untrusted producer's byte stream before treating length/pointer fields in it as authoritative.

### Impact Explanation
If an attacker can influence the bytes the `qr-code` (or another `SharedPort`) agent process writes back — e.g., by first exploiting a decoding bug in `rxing` while parsing a malicious QR code, which is within the allowed "QR/MECARD parsing" analog class — the broker process, which coordinates the full signup flow (`Orb`/`src/brokers/orb.rs`), would deserialize attacker-influenced archive bytes with `rkyv::archived_root` and no `bytecheck` validation. Depending on the corrupted relative-pointer fields, this can crash the trusted broker process (denial of service of an in-progress signup) or, in the worst case, cause out-of-bounds reads in the broker's memory space, which is a stronger-privileged process than the sandboxed agent — i.e., a process-to-process trust violation across the sandbox boundary, matching the reported bug's "process-to-process RCE between sandboxed tiles" impact class scoped to unprivileged-input trust boundary corruption.

### Likelihood Explanation
This requires first achieving a memory-corruption primitive inside the sandboxed `qr-code` process via a bug in the underlying QR decoding library (`rxing`) when parsing attacker-controlled QR content — a precondition, not something demonstrated here. Given that precondition, the deserialization path in `agentwire/src/port.rs` provides no additional validation layer, so the described lack of bounds/structure checking is directly confirmed in the code and is unconditionally reachable for any `SharedPort` agent's output channel, including `qr-code`.

### Recommendation
- Use `rkyv`'s checked deserialization APIs (`rkyv::validation::validators::DefaultValidator` + `rkyv::check_archived_root`, requiring the `bytecheck`/`validation` feature) instead of the unchecked `rkyv::archived_root` in `deserialize_message` (`agentwire/src/port.rs`), for any buffer whose producer is a separate process/sandbox.
- Bound-check the length prefix read from shared memory against the actual buffer capacity before slicing (`agentwire/src/port.rs:766-767`), rather than trusting it implicitly.
- Treat every `SharedPort` agent's output as untrusted input in the broker, applying the same "never trust cross-process data" discipline recommended in the original Firedancer fix.

### Proof of Concept
A concrete PoC requires two components: (1) a bug in `rxing`'s QR decoding of a maliciously crafted QR bitstream that lets an attacker overwrite the `qr-code` agent's `Output` shared-memory region (`SERIALIZED_OUTPUT_SIZE`, `src/agents/qr_code.rs:62`) with attacker-chosen bytes instead of a well-formed `rkyv` archive; and (2) demonstrating that `spawn_shared_tx_task`'s call to `deserialize_message::<T::Output>` (`agentwire/src/port.rs:815-823`) followed by `archived.deserialize(&mut SharedDeserializeMap::new())` panics or reads out-of-bounds when fed a byte sequence with a corrupted internal relative pointer/length inside an `ArchivedString`/`ArchivedVec` field, without any `bytecheck` validation gating it. Because component (1) is a separate, unproven vulnerability in a third-party dependency, this analog is reported as an architectural/defense-in-depth gap in the IPC trust boundary rather than an end-to-end exploited PoC.

### Citations

**File:** agentwire/src/agent/process.rs (L339-350)
```rust
fn sandbox_agent() -> std::io::Result<()> {
    #[allow(unused_mut)]
    let mut flags = CloneFlags::CLONE_NEWUSER | CloneFlags::CLONE_NEWIPC;
    #[cfg(feature = "sandbox-network")]
    {
        flags |= CloneFlags::CLONE_NEWNET;
    }
    match unshare(flags) {
        Ok(()) => Ok(()),
        Err(err) => Err(err.into()),
    }
}
```

**File:** agentwire/src/port.rs (L762-769)
```rust
unsafe fn deserialize_message<T>(buf: &[u8]) -> &T::Archived
where
    T: Archive + for<'a> Serialize<SharedSerializer<'a>>,
{
    let size = usize::from_ne_bytes(buf[..mem::size_of::<usize>()].try_into().unwrap());
    let bytes = &buf[mem::size_of::<usize>()..mem::size_of::<usize>() + size];
    unsafe { rkyv::archived_root::<T>(bytes) }
}
```

**File:** agentwire/src/port.rs (L815-823)
```rust
            let (value, source_ts) = unsafe {
                let shared_memory = addr as *mut SharedMemory<T>;
                let archived = deserialize_message::<T::Output>((*shared_memory).output());
                // Reuse of `SharedDeserializeMap` doesn't work
                let value = archived.deserialize(&mut SharedDeserializeMap::new()).unwrap();
                let source_ts = (*shared_memory).output_ts;
                sem_post(&mut (*shared_memory).output_tx).expect("semaphore failure");
                (value, source_ts)
            };
```

**File:** src/agents/qr_code.rs (L69-99)
```rust
impl agentwire::agent::Process for Agent {
    type Error = Error;

    fn run(self, mut port: RemoteInner<Self>) -> Result<(), Self::Error> {
        let mut qr_scanner = QrReader;
        loop {
            let input = port.recv();
            match input.value {
                ArchivedInput::Frame(frame) => {
                    match decode_rxing(
                        &mut qr_scanner,
                        frame.data().to_vec(),
                        frame.width(),
                        frame.height(),
                    ) {
                        Ok(output) => {
                            tracing::debug!("Decoded QR-code with rxing: {:?}", output.payload);
                            let chain = input.chain_fn();
                            port.try_send(&chain(output));
                        }
                        Err(e) => {
                            if !matches!(e, rxing::Exceptions::NotFoundException(_)) {
                                tracing::debug!("rxing error: {}", e);
                            }
                        }
                    }
                }
                ArchivedInput::Als(_) => {}
            }
        }
    }
```
