# [M] `array!` macro is unsound in presence of traits that implement methods it calls internally

## Summary
Severity: Medium
Advisory: GHSA-83gg-pwxf-jr89
Ecosystem: crates.io
Published: 2022-06-16
Source: https://github.com/advisories/GHSA-83gg-pwxf-jr89
Type: github-advisory

## Affected
- crates.io: `array-macro` — affected >=0.1.2 <1.0.5

## Details
Affected versions of this crate called some methods using auto-ref. The affected code looked like this.

```rust
let mut arr = $crate::__core::mem::MaybeUninit::uninit();
let mut vec = $crate::__ArrayVec::<T>::new(arr.as_mut_ptr() as *mut T);
```

In this case, the problem is that `as_mut_ptr` is a method of `&mut MaybeUninit`, not `MaybeUninit`. This made it possible for traits to hijack the method calls in order to cause unsoundness.

```rust
trait AsMutPtr<T> {
    fn as_mut_ptr(&self) -> *mut T;
}
impl<T> AsMutPtr<T> for std::mem::MaybeUninit<T> {
    fn as_mut_ptr(&self) -> *mut T {
        std::ptr::null_mut()
    }
}
array![0; 1];
```

The flaw was corrected by explicitly referencing variables in macro body in order to avoid auto-ref.

## References
- https://github.com/xfix/array-macro/commit/01940637dd8f3bfeeee3faf9639fa9ae52f19f4d
- https://github.com/rustsec/advisory-db/blob/main/crates/array-macro/RUSTSEC-2020-0161.md
- https://github.com/xfix/array-macro
- https://gitlab.com/KonradBorowski/array-macro/-/commit/01940637dd8f3bfeeee3faf9639fa9ae52f19f4d
- https://rustsec.org/advisories/RUSTSEC-2020-0161.html
