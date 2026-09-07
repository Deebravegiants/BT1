# [M] unbounded-spsc: Sender::send pointer-as-value transmute causes OOB read and fake-Arc drop under TX/RX race

## Summary
Severity: Medium
Advisory: GHSA-6m57-8r3p-pqx6
CVE: CVE-2026-46690
CWE: CWE-125, CWE-415, CWE-704, CWE-787
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:L/I:L/A:H (CVSS_V3)
Published: 2026-05-29
Source: https://github.com/advisories/GHSA-6m57-8r3p-pqx6
Type: github-advisory

## Affected
- crates.io: `unbounded-spsc` — affected >=0

## Details
## Summary

`Sender::send` in `src/lib.rs` contains an `unsafe` block in the `DISCONNECTED` arm that transmutes a **raw pointer** (`*mut Producer<T>`) into the bytes of a **value-level** `Consumer<T>`. The author's intent, visible in the surrounding comment at lines 386-390, was a value transmute. The shipped code is one level of indirection off.

The resulting `Consumer<T>` has its internal `Arc::ptr` set to the address of the `producer` field on the `Sender`, not the real `ArcInner<Buffer<T>>`. Every subsequent `consumer.try_pop()` walks `Buffer<T>` fields at offsets that lie inside the `Sender<T>` struct (over `send_new`, `inner`) and adjacent memory, an out-of-bounds read. When the fake `Consumer<T>` is dropped at the end of the `unsafe` block, its `Drop` calls `Arc::drop_in_place` on a non-`ArcInner` address: it decrements bytes that the type system treats as `strong_count: AtomicUsize` but that are actually the real `Arc::ptr` value of the `Sender`, and at zero count it calls `dealloc(Layout::for_value(...))` on an address the allocator never returned.

Reachable from 100% safe Rust through the canonical channel pattern: a `tx.send(msg)` that races with `rx.drop()`. This is consistent with the SIGSEGV that issue #3 reports in your own test suite.

## Affected code (0.2.0, master at `23a9ce7`)

```rust
// src/lib.rs:384-401
DISCONNECTED => {
    self.inner.counter.store (DISCONNECTED, Ordering::SeqCst);
    // We want to guarantee if a message was not received that we get it
    // back; since spsc::{Producer,Consumer} have the same
    // internal representation (as a singleton struct containing Arc
    // <Buffer <T>>), we can safely transmute the producer in order to
    // pop the message back if it was orphaned.
    unsafe {
      let consumer : spsc::Consumer <T>
        = std::mem::transmute (self.producer.get());     // <-- POINTER, not value
      let first    = consumer.try_pop();
      let second   = consumer.try_pop();
      assert!(second.is_none());                          // <-- line 396; smoking-gun assert
      if let Some(t) = first {
        return Err (SendError (t))
      }
    }
},
self.producer is UnsafeCell<spsc::Producer<T>> (line 29). UnsafeCell::<X>::get(&self) returns *mut X, a raw pointer, 8 bytes on 64-bit. The signature of transmute is transmute::<Src, Dst>(src: Src) -> Dst, so the call expands to transmute::<*mut spsc::Producer<T>, spsc::Consumer<T>>(self.producer.get()). 8 bytes of pointer are reinterpreted as the bytes of a Consumer<T>.

In bounded-spsc-queue-0.4.0, both Producer<T> and Consumer<T> are newtypes around Arc<Buffer<T>>, one pointer wide. The destination value therefore has Arc::ptr == &mut Producer<T> as *const ArcInner<Buffer<T>>. To be a valid Arc<Buffer<T>>, that pointer must point to ArcInner { strong: AtomicUsize, weak: AtomicUsize, data: Buffer<T> }, but it actually points to the start of Sender<T> (the producer field). The first 8 bytes there hold the real Arc::ptr. The fake Arc reads those bytes as strong_count. The fake try_pop() then reads Buffer<T> head/tail/data slots starting at offset 16 inside the Sender<T>, that is, inside the send_new and inner fields.

The author's intent (per the comment at lines 386-390) was a value-level transmute:

let producer_val: spsc::Producer<T> = std::ptr::read(self.producer.get());
let consumer    : spsc::Consumer<T> = std::mem::transmute(producer_val);
which is layout-sound iff Producer<T> and Consumer<T> have identical layouts (they do, both are single-Arc newtypes). The shipped code is one indirection off.

Reachability
The branch is not reachable single-threaded. Receiver::drop (line 332) stores connected = false before setting counter = DISCONNECTED; Sender::send (line 359) early-returns on connected == false. The trigger is a TOCTOU race:

Sender's self.inner.connected.load(SeqCst) reads true.
Receiver-drop runs: stores connected = false and counter.compare_exchange(_, DISCONNECTED, SeqCst, SeqCst).
Sender's self.inner.counter.fetch_add(1, SeqCst) (line 379) sees DISCONNECTED and enters the unsafe block.
Under heavy contention this reproduces ~3/10 trials in release mode.

Proof of concept (race shape)
// Cargo.toml: unbounded-spsc = "0.2"
use std::thread;
use unbounded_spsc::channel;

fn main() {
    for trial in 0..500 {
        let (tx, rx) = channel::<Box<u64>>();
        let started = std::sync::Arc::new(
            std::sync::atomic::AtomicBool::new(false));
        let s = started.clone();
        let h = thread::spawn(move || {
            s.store(true, std::sync::atomic::Ordering::SeqCst);
            for _ in 0..10_000 {
                let _ = tx.send(Box::new(0xDEAD_BEEF));
            }
        });
        while !started.load(std::sync::atomic::Ordering::SeqCst) {
            std::hint::spin_loop();
        }
        drop(rx);
        let _ = h.join();
        eprintln!("trial {trial} ok");
    }
}
Observed:

Release-mode (no sanitizer): Segmentation fault (core dumped) reliably within a few trials. The non-segfaulting trials are masked by the separate send_new.send(new_consumer).unwrap() panic, see Secondary defect below.
-Zsanitizer=address -Zbuild-std (nightly): ASan reports stack-buffer-overflow / stack-use-after-scope from the fake-Consumer's try_pop walking off the Sender frame.
This matches the SIGSEGV reported in your own issue #3.

Smoking-gun upstream evidence
src/lib.rs:975 in the project's test suite carries a TODO:

// TODO: failures
// - failed with assertion on line 394 in send fn
//   assert!(second.is_none())
That is the assertion site of the transmute block (line 396 in 0.2.0 / master). You have observed try_pop() returning a non-None value where logically there should be none, which is exactly what reading random bytes from the Sender's send_new / inner fields produces, and the symptom has been marked as a flaky test rather than recognised as UB.

Impact
Reachable from 100% safe Rust. Concrete UB primitives:

OOB read of bytes adjacent to the Sender<T> struct via fake Consumer<T>::try_pop(). The popped T is returned through Err(SendError(t)) to safe-code, an allocator-layout-controlled leak of process memory.
OOB write via fake Arc::drop AtomicUsize::fetch_sub on bytes that are actually the real Arc::ptr value of the Sender.
Allocator corruption via fake Arc::drop calling dealloc(Layout::for_value(...)) on a non-allocated address. The Sender struct holds the real Arc<Inner> immediately after the producer field; the deallocator call therefore uses a layout the allocator never allocated, which on glibc is a confirmed double-free / arbitrary-bucket-poisoning primitive, and on hardened allocators (jemalloc-secure, mimalloc-secure) is an immediate abort.
Secondary defect (same call path, bonus)
Sender::send line 369:

self.send_new.send(new_consumer).unwrap();
When the Sender's message queue is full, a fresh bounded_spsc_queue::Channel is allocated and the new Consumer<T> is shipped over an std::sync::mpsc side-channel to the Receiver. If the Receiver has already been dropped, receive_new is gone and this unwrap() panics. The panic surfaces in your own test suite, issue #2 (tests::port_gone_concurrent panicked at src/lib.rs:369) and the in-source TODO at lines 365-368 already note the question "Are we sure that this is safe to unwrap or should we handle the result explicitly ?".

The fix is to return Err(SendError(t)) instead of unwrapping, same shape as the channel-closed result the function already returns on the connected-false path. This is not a memory-safety defect, only a panic, but it lives on the same TX/RX-race code path and a single coordinated patch can address both. Filing it here so we cover the full call site in one cycle.

Suggested patch (primary defect)
Replace the pointer-as-value transmute with a value-level read and a ManuallyDrop to suppress the alias's Producer::drop on subsequent exit:

unsafe {
    use core::mem::ManuallyDrop;

    // Sound value-level transmute: Producer<T> and Consumer<T> are both
    // newtypes around Arc<Buffer<T>>, so the value layouts match.
    // ptr::read takes ownership of the Producer's bytes without running
    // Producer's Drop.
    let producer_val: spsc::Producer<T> = std::ptr::read(self.producer.get());
    let consumer    : spsc::Consumer<T> = std::mem::transmute(producer_val);

    let first  = consumer.try_pop();
    let second = consumer.try_pop();
    assert!(second.is_none());
    if let Some(t) = first {
        return Err(SendError(t));
    }

    // consumer drops here; the same memory backs `producer`, so suppress
    // the double Producer drop:
    let _ = ManuallyDrop::new(consumer);
}
Cleaner: restructure Sender<T> to hold producer and consumer in a private enum Endpoint<T> so no transmute is required, or use the bounded_spsc_queue::Producer<T>::reclaim() escape hatch if available.

Suggested patch (secondary defect)
if let Err(std::sync::mpsc::SendError(_)) = self.send_new.send(new_consumer) {
    // Receiver has been dropped: take the message back as the public
    // SendError, the same way the connected==false early-return does.
    return Err(SendError(t));
}
Regression test (release-mode, race shape)
#[test]
fn race_disconnect_does_not_corrupt_sender_or_abort() {
    for _ in 0..200 {
        let (tx, rx) = unbounded_spsc::channel::<Box<u64>>();
        let h = std::thread::spawn(move || {
            for _ in 0..10_000 {
                let _ = tx.send(Box::new(0xDEAD_BEEF));
            }
        });
        drop(rx);
        h.join().unwrap();
    }
}
Reverse dependencies
Two crates on crates.io depend on unbounded-spsc, both owned by you: apis (process-calculus framework) and gooey-rs (tile-UI library, unbounded-spsc gated behind opengl/fmod features). The OpenGL/FMOD callback-mailbox use is a natural rx-drop-during-tx-send scenario at scene-graph teardown. A single coordinated bump cycle is feasible.

Researcher
Berkant Koc me@berkoc.com
PGP: 0C588DFD76204987284213EA0AC529C41F8AA5D6

## References
- https://github.com/spearman/unbounded-spsc/security/advisories/GHSA-6m57-8r3p-pqx6
- https://nvd.nist.gov/vuln/detail/CVE-2026-46690
- https://github.com/spearman/unbounded-spsc
