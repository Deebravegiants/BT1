# [M] Centralization attack vectors are present in the code

## Summary
Severity: Medium
Contest weight: 0.0633
Dataset id: 3668
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
There are multiple centralization attack vectors present in the contracts. Examples are: HibernationDen::setVRFConfig - updating this with arbitrary values can break the game HoneyJarPortal::setHibernationDen - updating it to a random address will DoS the game HoneyJarPortal::setAdapterParams - using too low of a gasLimit value will result in out of gas reverts

## Recommendation
Make the methods callable only once or add them to the constructors/initializer methods.
