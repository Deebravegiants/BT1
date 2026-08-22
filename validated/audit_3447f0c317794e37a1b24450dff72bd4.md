Now I have enough evidence to establish this analog concretely.

### Title
Unvalidated size field in IPC shared-memory deserialization allows QR-code agent to crash orb-core - ([File: agentwire/src/port.rs])

### Summary
The `MsgReceiver.sol` bug is caused by trusting attacker-influenced, unbounded external data (the returned data size) without validating it before use, leading to resource exhaustion and denial of service. The analogous pattern in orb-core is `deserialize_message` in `agentwire/src/port.rs`, which reads a `size` value embedded in a shared-memory buffer written by a process-based agent, and slices the buffer using that `size` without validating it against the buffer's actual allocated capacity (`SERIALIZED_INPUT_SIZE`/`SERIALIZED_OUTPUT_SIZE`).

### Finding Description
`deserialize_message` reads an untrusted length prefix from the shared-memory buffer and directly indexes into the buffer using it: [1](#0-0) 

This `buf` is the fixed-size shared-memory region (`SharedMemory::output`/`SharedMemory::input`) written to by a process-based agent running in a separate, sandboxed OS process: [2](#0-1) 

Process-based agents are explicitly documented as running "untrusted or unreliable code": [3](#0-2) 

One such agent is `qr_code::Agent`, which decodes QR codes from camera frames using the third-party `rxing` decoding library, and thus processes attacker/user-controlled QR-code image content inside its own subprocess before writing the decoded result back through this shared-memory channel: [4](#0-3) 

If the agent process is compromised (e.g. via a memory-corruption bug in the QR decoder triggered by a maliciously crafted QR image, similar in spirit to `Eve`'s hostile contract in the Solidity report), it can write an arbitrary `size` value into the shared-memory header. Because `deserialize_message` does not bound-check `size` against `SERIALIZED_OUTPUT_SIZE`/`SERIALIZED_INPUT_SIZE` before slicing, the broker process reading it (`spawn_shared_tx_task`/`RemoteInner::recv`) will panic on out-of-bounds slice indexing: [5](#0-4) 

A panic in this code path (invoked from `task::spawn_local`) crashes the orb-core main process, exactly mirroring the reported bug class: an unvalidated size derived from a boundary-crossing, potentially adversarial component is used to index/allocate without validation, producing an unbounded resource/crash condition rather than a controlled failure.

### Impact Explanation
A crash of the main orb-core process during a signup session is a denial of service against the entire biometric signup pipeline — it aborts an in-progress signup (potential cross-signup state bleed on restart) and repeats indefinitely if the malicious QR content is presented again, matching the exploit scenario of "the relayer continues to propagate the transaction without success" in the original report, here as "orb-core keeps restarting/crashing on the same malicious QR input."

### Likelihood Explanation
The QR-code agent is on the direct signup entry path — the operator/user QR-code scan step run at the start of every signup, driven directly by camera frames of an untrusted, user-presented QR code. Reaching this bug requires first finding/crafting an input that corrupts the agent's process state such that the `size` prefix it writes is wrong, which requires an additional memory-safety bug in the decoding path (`rxing`) or the serialization logic. This is not a trivial single-input exploit, which lowers overall likelihood.

### Recommendation
- Short term: In `deserialize_message`, validate `size` is `<= buf.len() - size_of::<usize>()` before slicing, and return an error/drop the message instead of panicking on invalid size.
- Long term: Treat all data crossing the process-agent shared-memory boundary as untrusted input (the same threat model already documented in `agentwire`'s own docs for "untrusted or unreliable code"), and add fuzzing/bounds tests for `serialize_message`/`deserialize_message` round trips with corrupted size prefixes.

### Proof of Concept
1. A process-based agent (e.g. `qr_code::Agent`, or any other `Process` agent) writes to its output shared-memory buffer via `serialize_message`, which writes an 8-byte little/native-endian `size` header followed by the serialized payload.
2. If, due to a bug in the agent's own code (e.g., a corrupted intermediate state after processing an adversarial QR image), the agent process ends up writing (directly or via a corrupted serializer state) a `size` value larger than `SERIALIZED_OUTPUT_SIZE - size_of::<usize>()`.
3. On the broker side, `spawn_shared_tx_task` calls `deserialize_message::<T::Output>((*shared_memory).output())`, which computes `bytes = &buf[8..8 + size]`; because `size` was not validated against `buf.len()`, this slice operation panics with an out-of-bounds index.
4. The panic occurs inside a `tokio::task::spawn_local`'d task in the broker's dedicated IPC thread; depending on panic handling configuration, this aborts the orb-core process, terminating the active signup and any subsequent restarts repeat the same failure if triggered by persistent adversarial input.

### Citations

**File:** agentwire/src/port.rs (L596-612)
```rust
    unsafe fn input(&mut self, n: usize) -> &mut [u8] {
        unsafe {
            slice::from_raw_parts_mut(
                ptr::addr_of_mut!(*self).add(1).cast::<u8>().add(T::SERIALIZED_INPUT_SIZE * n),
                T::SERIALIZED_INPUT_SIZE,
            )
        }
    }

    unsafe fn output(&mut self) -> &mut [u8] {
        unsafe {
            slice::from_raw_parts_mut(
                ptr::addr_of_mut!(*self).add(1).cast::<u8>().add(T::SERIALIZED_INPUT_SIZE * 2),
                T::SERIALIZED_OUTPUT_SIZE,
            )
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

**File:** agentwire/src/lib.rs (L121-126)
```rust
//! # Process-based agents
//!
//! Process-based agents are agents that run inside their own separate
//! processes. They are isolated from the broker and other agents, and can be
//! used to run untrusted or unreliable code.
//!
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
