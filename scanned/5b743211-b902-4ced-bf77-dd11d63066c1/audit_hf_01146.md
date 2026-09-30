# [M] Memory pointer can overflow in hintstore

## Summary
Severity: Medium
Reporter: Leo Alt
Contest weight: 0.1483
Dataset id: 4895
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability is an unchecked memory pointer overflow in a hint‑store mechanism that allows a caller to write a 32‑bit value to an arbitrary memory address. The contract expects the address supplied to the hint function to be limited to a 29‑bit range (the last limb of the pointer is supposed to be only 5 bits), but the implementation does not enforce this constraint. As a result, an attacker can craft a pointer whose high bits overflow, effectively adding an arbitrary offset to a legitimate address. By combining the overflowed pointer with the location of a variable that is under the attacker’s control (for example the input value of the transaction), the hint write can be redirected to any chosen storage slot, stack variable, or other critical data structure. This enables the attacker to overwrite selected memory locations, such as balances, access‑control flags, or accounting variables, leading to state corruption, loss of funds, or disruption of protocol logic. The exploit works when the hint function is invoked with a user‑controlled address and the contract fails to mask or validate the pointer; the overflow occurs at runtime and does not trigger a revert, making the effect subtle. The issue was discovered during a manual audit of the OpenVM hint interface, where a proof‑of‑concept written in Rust demonstrated that providing a specially crafted address (p = (1<<31)-(1<<27)+1) and adding the address of a variable caused the hint write to modify that variable, confirming the overflow. The bug can be hard to notice because the hint mechanism is intended for debugging and does not produce obvious error messages; the corrupted state may only become apparent later when balances are wrong or contract functions behave unexpectedly. From a user’s point of view the symptom may be that a transaction that should leave their balance unchanged instead sets it to zero, or that a refund amount is missing despite the contract logic indicating it should be paid. The expectation that the hint call is harmless is violated, and the accounting assumptions of the protocol are broken. To remediate the issue the contract should enforce the 5‑bit limit on the pointer’s last limb, for example by masking the address with a 0x1F mask or by rejecting any pointer that exceeds the 29‑bit range, thereby preventing arbitrary memory writes.

## Proof of Concept
The proof of concept below shows the case described above, where an attacker uses the hint function directly with an address that overflows p.  
// src/main.rs  
use openvm::io::read;  
extern crate openvm;  
use openvm_rv32im_guest::hint_buffer_u32;  
extern crate openvm_rv32im_guest;  
fn main() {  
let n: u32 = read();  
let old_n = n.clone();  
let p: u32 = (1 << 31) - (1 << 27) + 1;  
let addr = p as *mut u32;  
let n_ptr = &n as *const u32 as usize;  
let overflow_addr = (addr as usize) + n_ptr;  
let overflow_ptr = overflow_addr as *mut u32;  
hint_buffer_u32!(overflow_ptr, 1);  
assert!(n != old_n);  
}

## Recommendation
Constrain the last limb to 5 bits (memory addresses are constrained to 29 bits).
