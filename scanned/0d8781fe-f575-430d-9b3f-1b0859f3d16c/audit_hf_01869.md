# [M] M-6 Tests do not work

## Summary
Severity: Medium
Contest weight: 0.0246
Dataset id: 10401
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability consists of a non‑functional test suite for the protocol. Because the automated tests fail to compile or execute, developers cannot verify that the contract logic satisfies its specifications, nor can they generate reliable proof‑of‑concept attacks. The root cause is that the test files are either missing, incorrectly configured, or depend on unavailable libraries, causing the test runner to abort before any assertions are evaluated. An attacker can exploit this situation by deploying the contract without any prior validation; hidden bugs such as arithmetic errors, access‑control flaws, or re‑entrancy vulnerabilities may remain undetected. The impact is that users may interact with a contract that behaves incorrectly, leading to lost funds, unexpected zero balances, or failed refunds. The condition under which the issue manifests is any development or CI environment where the test command is invoked – the suite immediately exits with errors, providing no coverage metrics. All participants – developers, auditors, and end‑users – are affected because the lack of testing undermines confidence in the protocol’s safety. The problem was discovered during a manual audit when the auditors attempted to run the provided test scripts and observed that they never produced results. The issue is hard to notice because a repository may appear complete, yet the absence of passing tests gives a false sense of security. To remediate, the team should create a comprehensive set of unit and integration tests, configure the testing framework correctly, ensure all dependencies are installed, and integrate the suite into a continuous‑integration pipeline so that test failures block deployment. In generic terms, this is a test‑suite failure or missing test coverage bug that violates the fundamental security engineering practice of verifying contract behavior before launch.

## Recommendation
We recommend prioritizing, preparing, and setting up all the tests before the protocol deployment.
