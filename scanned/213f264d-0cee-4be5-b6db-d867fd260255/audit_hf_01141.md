# [H] Heap pointer can overflow

## Summary
Severity: High
Reporter: Leo Alt
Contest weight: 0.2980
Dataset id: 4877
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability is a heap pointer overflow in the memory allocator used by the OpenVM platform. The allocator updates an internal heap pointer when a new allocation request is made, but it does not verify that the addition of the requested size will stay within the addressable range of the heap. Because the pointer arithmetic is performed using unsigned 32‑bit arithmetic, a sufficiently large allocation size can cause the pointer to wrap around to a low address, effectively moving the heap pointer backwards. This overflow enables an attacker to request an allocation that overlaps previously allocated memory regions, such as vectors stored on the heap. By allocating a chunk whose size is calculated as the maximum unsigned integer minus the current heap pointer, the attacker forces the pointer to wrap and then allocates another chunk at an address that is deliberately chosen to overlap an existing vector. The overlapping allocation corrupts the contents of the original vector without triggering any explicit error, allowing assertions that compare the vectors to succeed even though the underlying data has been altered. The impact is that an attacker can manipulate arbitrary areas of the heap, overwrite critical contract state, and potentially cause loss of funds, incorrect accounting, or execution of unintended logic. The condition occurs whenever the allocator’s pointer update is performed without a bounds check, which is typical during any dynamic memory allocation performed by the contract or by external callers that can influence allocation size. Users of the contract, including regular participants and the protocol itself, are affected because corrupted state may lead to missing refunds, zero balances, or other unexpected behavior visible at the UI level (e.g., a user expects a token transfer but receives nothing). The issue was discovered during a manual audit that exercised the allocator with extreme allocation sizes; the proof‑of‑concept demonstrates that two assertions that should fail actually pass when the overflow is triggered, indicating hidden memory overlap. The bug is hard to notice because the allocator does not emit any error on overflow and the resulting state corruption may only manifest as subtle logic errors rather than outright crashes. Conceptually, the fix is to treat this as a classic heap overflow vulnerability: the allocator must perform an overflow check before updating the heap pointer and must reject allocation requests that would cause the pointer to exceed the maximum addressable range. Adding explicit bounds validation to the pointer arithmetic eliminates the possibility of overlapping allocations and restores the integrity of heap‑based data structures.

## Proof of Concept
In the code below, both assertions at the end succeed but should fail without the
exploit. In fact, commenting out line _alloc_overflow makes the execution fail.
// src/main.rs
use openvm::io::{read, read_vec, reveal};
extern crate openvm;
use openvm::platform::memory::sys_alloc_aligned;
extern crate openvm_rv32im_guest;
extern crate alloc;
openvm::entry!(main);
fn main() {
let n: u32 = read();
let c = n * 2;
let mut v1: Vec<u32> = Vec::new();
v1.push(c as u32);
let old_v1_0 = v1[0];
let heap_ptr = unsafe { sys_alloc_aligned(4, 4) };
let missing = u32::MAX - (heap_ptr as u32);
let _alloc_overflow = unsafe { sys_alloc_aligned(missing as usize, 4) };
let _alloc_overlap = unsafe { sys_alloc_aligned((v1.as_ptr() as usize) - 4, 4) };
let mut v2: Vec<u32> = Vec::new();
v2.push((c + 1) as u32);
assert_eq!(v1, v2);
assert!(old_v1_0 != v1[0]);
}

## Recommendation
Add overflow checks to the allocator heap pointer updates.
