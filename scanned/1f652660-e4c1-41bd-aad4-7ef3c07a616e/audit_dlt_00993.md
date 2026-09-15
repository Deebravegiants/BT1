# [?] fix[codegen]: panic on potential subscript eval order issue (#4159)

## Summary
Severity: Unknown
Chain: Vyper
Component: vyperlang/vyper
Published: 2024-06-19
Source: https://github.com/vyperlang/vyper/commit/4594f8badf13a583875f8891698cd3bbefb1c787
Type: security-commit

## Details
fix[codegen]: panic on potential subscript eval order issue (#4159)

subscript expressions have an evaluation order issue when
evaluation of the index (i.e. `node.index`) modifies the parent
(i.e. `node.value`). because the evaluation of the parent is
interleaved with evaluation of the index, it can result in "invalid"
reads where the length check occurs before evaluation of the index, but
the data read occurs afterwards. if evaluation of the index results in
modification of the container size for instance, the data read from the
container can happen on a dangling reference.

another variant of this issue would be accessing
`self.nested_array.pop().append(...)`; however, this currently happens
to be blocked by a panic in the frontend.

this commit conservatively blocks compilation if the preconditions for
the interleaved evaluation are detected. POC tests that the appropriate
panics are generated are included as well.

---------

Co-authored-by: trocher <trooocher@proton.me>
Co-authored-by: Hubert Ritzdorf <hubert.ritzdorf@chainsecurity.com>
Co-authored-by: cyberthirst <cyberthirst.eth@gmail.com>
