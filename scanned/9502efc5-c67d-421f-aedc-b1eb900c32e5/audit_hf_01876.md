# [M] M-5 Not All the Tests are Passing

## Summary
Severity: Medium
Contest weight: 0.0226
Dataset id: 10440
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The issue identified is an incomplete and failing test suite for the smart‑contract protocol. The root cause is that several test cases either do not compile, produce runtime errors, or are missing entirely, which prevents the auditors from measuring test coverage and from constructing reliable proof‑of‑concept attacks. Because the test harness does not execute successfully, developers cannot verify that the contract logic conforms to its specification, nor can they confirm that edge‑case handling (such as re‑entrancy, overflow, or permission checks) behaves correctly. An attacker could therefore interact with the deployed contract in ways that were never exercised during testing, potentially triggering unexpected state changes, loss of funds, or denial of service. The impact is that the protocol may contain hidden bugs that only surface after deployment, exposing users’ assets and undermining confidence in the system. This condition occurs during the pre‑deployment phase when the repository contains failing or absent tests, and it affects anyone who relies on the contract – developers, auditors, and end‑users. The problem was discovered during a formal security audit when the auditors attempted to run the provided test suite and observed multiple failures, making it impossible to generate coverage metrics or PoC scripts. The difficulty in noticing the problem stems from the fact that failing tests can be overlooked if the development team assumes they are non‑critical or if continuous‑integration pipelines are not enforced. To remediate, the team should rewrite or fix the failing tests, add missing test cases that cover all public functions, boundary conditions, and failure paths, and enforce a policy that the entire test suite must pass before any contract is merged or deployed. In generic terms, this is a test‑coverage deficiency that violates the fundamental security practice of exhaustive validation, leading to a situation where “funds disappear” or “transactions revert unexpectedly” because the contract’s behavior under certain inputs has never been verified.

## Recommendation
We recommend preparing and setting up all the tests before the protocol deployment.
