# [H] Duplicate Advisory: web3-utils Prototype Pollution vulnerability

## Summary
Severity: High
Chain: web3-utils
Component: web3-utils
CWE: Improperly Controlled Modification of Object Prototype Attributes ('Prototype Pollution')
Published: 2024-03-25
Source: https://github.com/advisories/GHSA-87qp-7cw8-8q9c
Type: github-advisory

## Details
## Duplicate Advisory
This advisory has been withdrawn because it is a duplicate of GHSA-2g4c-8fpm-c46v. This link is maintained to preserve external references.

## Original Description
Versions of the package web3-utils before 4.2.1 are vulnerable to Prototype Pollution via the utility functions format and mergeDeep, due to insecure recursive merge.
An attacker can manipulate an object's prototype, potentially leading to the alteration of the behavior of all objects inheriting from the affected prototype by passing specially crafted input to these functions.
