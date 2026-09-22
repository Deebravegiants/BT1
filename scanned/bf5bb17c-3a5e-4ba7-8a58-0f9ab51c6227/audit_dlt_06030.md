# [?] fix(starfish): harden consensus against panic-inducing peer messages (#11202)

## Summary
Severity: Unknown
Chain: IOTA
Component: iotaledger/iota
Published: 2026-04-09
Source: https://github.com/iotaledger/iota/commit/702e8f7c2ccb592bcbf7f2e3c386641372e6c026
Type: security-commit

## Details
fix(starfish): harden consensus against panic-inducing peer messages (#11202)

# Description of change

Replace panic paths with proper error propagation across peer-facing
Starfish code paths, hardening the node against malformed or malicious
messages from peers.

**Changes:**
- Replace `.expect()` with `?` on peer-triggered merkle/encoding
computations in authority service and commit syncer
- Validate authority indices from untrusted peer messages (block
bundles, block verifier, cordial knowledge)
- Replace `unimplemented!()` macro with gRPC `Status::unimplemented` in
deprecated RPC

## Links to any relevant issues

Fixes #11201

## How the change has been tested

- [x] Basic tests (linting, compilation, formatting, unit/integration
tests)
- [x] I have added tests that prove my fix is effective or that my
feature works
- [x] I have checked that new and existing unit tests pass locally with
my changes
