[1](#0-0) [2](#0-1)

### Citations

**File:** types/src/error.rs (L71-101)
```rust
impl<T: std::fmt::Debug> From<PanicError> for PanicOr<T> {
    fn from(err: PanicError) -> Self {
        match err {
            PanicError::CodeInvariantError(e) => PanicOr::CodeInvariantError(e),
        }
    }
}

impl<T: std::fmt::Debug> From<&PanicOr<T>> for StatusCode {
    fn from(err: &PanicOr<T>) -> Self {
        match err {
            PanicOr::CodeInvariantError(_) => {
                StatusCode::DELAYED_FIELD_OR_BLOCKSTM_CODE_INVARIANT_ERROR
            },
            PanicOr::Or(_) => StatusCode::SPECULATIVE_EXECUTION_ABORT_ERROR,
        }
    }
}

impl<T: std::fmt::Debug> From<PanicOr<T>> for PartialVMError {
    fn from(err: PanicOr<T>) -> Self {
        match err {
            PanicOr::CodeInvariantError(msg) => {
                PartialVMError::new(StatusCode::DELAYED_FIELD_OR_BLOCKSTM_CODE_INVARIANT_ERROR)
                    .with_message(msg)
            },
            PanicOr::Or(err) => PartialVMError::new(StatusCode::SPECULATIVE_EXECUTION_ABORT_ERROR)
                .with_message(format!("{:?}", err)),
        }
    }
}
```

**File:** aptos-move/block-executor/src/errors.rs (L42-54)
```rust
impl<E> From<PanicError> for BlockExecutionError<E> {
    fn from(err: PanicError) -> Self {
        BlockExecutionError::FatalBlockExecutorError(err)
    }
}

impl<E> From<PanicError> for SequentialBlockExecutionError<E> {
    fn from(err: PanicError) -> Self {
        SequentialBlockExecutionError::ErrorToReturn(BlockExecutionError::FatalBlockExecutorError(
            err,
        ))
    }
}
```
