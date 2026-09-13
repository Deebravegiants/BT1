# [H] The rs-soroban-sdk #[contractimpl] macro calls inherent function instead of trait function when names collide

## Summary
Severity: High
Chain: soroban-sdk-macros
Component: soroban-sdk-macros, soroban-sdk-macros, soroban-sdk-macros
CVE: CVE-2026-26267
CWE: Always-Incorrect Control Flow Implementation
Published: 2026-02-17
Source: https://github.com/advisories/GHSA-4chv-4c6w-w254
Type: github-advisory

## Details
### Impact

The `#[contractimpl]` macro contains a bug in how it wires up function calls.

In Rust, you can define functions on a type in two ways:
- Directly on the type as an inherent function:
  ```rust
  impl MyContract {
      fn value() { ... }
  }
  ```
- Through a trait
  ```rust
  impl Trait for MyContract {
      fn value() { ... }
  }
  ```

These are two separate functions that happen to share the same name. Rust has rules for which one gets called. When you write `MyContract::value()`, Rust always picks the one defined directly on the type, not the trait version.

The bug is that `#[contractimpl]` generates code that uses `MyContract::value()` style calls even when it's processing the trait version. This means if an inherent function is also defined with the same name, the inherent function gets called instead of the trait function.

This means the Wasm-exported entry point silently calls the wrong function when two conditions are met simultaneously:
1. A `impl Trait for MyContract` block is defined with one or more functions, with `#[contractimpl]` applied.
2. A `impl MyContract` block is defined with one or more identically named functions, without `#[contractimpl]` applied.

If the trait version contains important security checks, such as verifying the caller is authorized, that the inherent version does not, those checks are bypassed. Anyone interacting with the contract through its public interface will call the wrong function.

For example:

```rust
#[contract]
pub struct Contract;

impl Contract {
    /// Inherent function — returns 1.
    /// Bug: The macro-generated WASM export is wired up to call this function.
    pub fn value() -> u32 {
        1
    }
}

pub trait Trait {
    fn value(env: Env) -> u32;
}

#[contractimpl]
impl Trait for MyContract {
    /// Trait implementation — returns 2.
    /// Fix: The macro-generated WASM export should call this function.
    fn value() -> u32 {
        2
    }
}
```

### Patches

The problem is patched in `soroban-sdk-macros` version **25.1.1**. The fix changes the generated call from `<Type>::func()` to `<Type as Trait>::func()` when processing trait implementations, ensuring Rust resolves to the trait associated function regardless of whether an inherent function with the same name exists.

Users should upgrade to `soroban-sdk-macros` **>= 25.1.1** and recompile their contracts.

### Workarounds

If upgrading is not immediately possible, contract developers can avoid the issue by ensuring that no inherent associated function on the contract type shares a name with any function in the trait implementation. Renaming or removing the conflicting inherent function eliminates the ambiguity and causes the macro-generated code to correctly resolve to the trait function.
