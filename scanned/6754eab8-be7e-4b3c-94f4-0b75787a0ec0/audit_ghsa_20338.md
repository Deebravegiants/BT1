# [H] Use after free in Neon external buffers

## Summary
Severity: High
Advisory: GHSA-8mj7-wxmc-f424
Ecosystem: crates.io
Published: 2022-06-17
Source: https://github.com/advisories/GHSA-8mj7-wxmc-f424
Type: github-advisory

## Affected
- crates.io: `neon` — affected >=0.8.0 <0.10.1

## Details
Neon provides functionality for creating JavaScript `ArrayBuffer` (and the `Buffer` subtype) instances backed by bytes allocated outside of V8/Node. The [`JsArrayBuffer::external`](https://docs.rs/neon/0.10.0/neon/types/struct.JsArrayBuffer.html#method.external) and [`JsBuffer::external`](https://docs.rs/neon/0.10.0/neon/types/struct.JsBuffer.html#method.external) did not require `T: 'static` prior to Neon `0.10.1`. This allowed creating an externally backed buffer from types that may be freed while they are still referenced by a JavaScript `ArrayBuffer`.

The following example demonstrates use after free. It compiles on versions `<0.10.1` and fails to compile afterward.

```rust
pub fn soundness_hole(mut cx: FunctionContext) -> JsResult<JsArrayBuffer> {
    let mut data = vec![0u8, 1, 2, 3];
    
    // Creating an external from `&mut [u8]` instead of `Vec<u8>` since there is a blanket impl
    // of `AsMut<T> for &mut T`
    let buf = JsArrayBuffer::external(&mut cx, data.as_mut_slice());

    // `buf` is still holding a reference to `data`!
    drop(data);

    Ok(buf)
}
```

## References
- https://github.com/neon-bindings/neon/issues/896
- https://github.com/neon-bindings/neon
- https://rustsec.org/advisories/RUSTSEC-2022-0028.html
