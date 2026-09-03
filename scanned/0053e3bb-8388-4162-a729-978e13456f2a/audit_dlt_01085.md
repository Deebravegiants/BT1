# [M] Unsound API in `secp256k1` allows use-after-free and invalid deallocation from safe code

## Summary
Severity: Medium
Chain: secp256k1
Component: secp256k1, secp256k1, secp256k1
Published: 2022-12-08
Source: https://github.com/advisories/GHSA-969w-q74q-9j8v
Type: github-advisory

## Details
Because of incorrect bounds on method `Secp256k1::preallocated_gen_new` it was possible to cause use-after-free from safe consumer code. It was also possible to "free" memory not allocated by the appropriate allocator.

The method takes a place for storing the context as a mutable reference and returns context containing that reference. Because the code internally uses `unsafe` and the bounds were incorrect it was possible to create a context that outlived the passed reference (e.g. `'static`). Because the context can alternatively carry heap-allocated pointer freed on drop it was possible to "deallocate" a pointer that wasn't returned from appropriate allocator. The code decides whether to free the memory based on type parameter but because of missing bound it was possible to construct the context with invalid parameter.

You are unaffected if you either

* don't call `Secp256k1::preallocated_gen_new`
* manually checked that your usage of the method is sound
* upgraded to the patched version of `secp256k1` (recommended)

The patched version uses correct bounds which means it is API-breaking. This effectively means adopting the policy of Rust lang itself allowing API-breaking changes to fix soundness bugs. Note however that valid straigthforward usage of the code will continue to compile. Only unsound code or code that propagates the bound in custom generics will fail to compile. If the code is sound fixing the bounds should be sufficient to make the code compile.

See the [GitHub issue](https://github.com/rust-bitcoin/rust-secp256k1/issues/543) for example "exploit" code and further discussion.
