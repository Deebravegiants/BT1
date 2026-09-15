# [?] Fix GHOSTDAG K violation panic and refactor DAG parameters

## Summary
Severity: Unknown
Chain: Starcoin
Component: starcoinorg/starcoin
Published: 2025-08-27
Source: https://github.com/starcoinorg/starcoin/commit/9b6f582a34d95690444e9a1183f6a3fbdc84fe72
Type: security-commit

## Details
Fix GHOSTDAG K violation panic and refactor DAG parameters

  - Replace assert with Red state return to prevent DoS attacks
  - Add max_parents_count to BlockDAG, validate K >= max_parents
  - Remove hardcoded constants, use genesis config for K value
  - Test methods use fixed values, production uses config
