# [C] Remote code execution in pytorch lightning

## Summary
Severity: Critical
Chain: lightning
Component: lightning
CVE: CVE-2024-5452
CWE: Improper Control of Dynamically-Managed Code Resources, Improperly Controlled Modification of Dynamically-Determined Object Attributes
Published: 2024-06-06
Source: https://github.com/advisories/GHSA-cgwc-qvrx-rf7f
Type: github-advisory

## Details
A remote code execution (RCE) vulnerability exists in the lightning-ai/pytorch-lightning library version 2.2.1 due to improper handling of deserialized user input and mismanagement of dunder attributes by the `deepdiff` library. The library uses `deepdiff.Delta` objects to modify application state based on frontend actions. However, it is possible to bypass the intended restrictions on modifying dunder attributes, allowing an attacker to construct a serialized delta that passes the deserializer whitelist and contains dunder attributes. When processed, this can be exploited to access other modules, classes, and instances, leading to arbitrary attribute write and total RCE on any self-hosted pytorch-lightning application in its default configuration, as the delta endpoint is enabled by default.
