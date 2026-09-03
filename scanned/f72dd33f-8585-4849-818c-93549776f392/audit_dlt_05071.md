# [M] Out-of-memory during deserialization with crafted inputs

## Summary
Severity: Medium
Chain: ZK
Component: Consensys/gnark
CVE: CVE-2024-50354
Published: 2024-10-31
Source: https://github.com/Consensys/gnark/security/advisories/GHSA-cph5-3pgr-c82g
Type: github-advisory

## Details
Thanks @pventuzelo for reporting.

From the correspondence:

> Hi,
> 
> We (Fuzzinglabs & Lambdaclass) found that during deserialization of certain files representing a `VerifyingKey`, an excessive memory allocation is happening consuming a lot of resources and even triggering a crash with the error `fatal error: runtime: out of memory`.
> 
> Please find the details below:
> 
> ## Vulnerability Details
> 
> - **Severity:** Critical -> DoS
> - **Affected Component:** Deserialization
> 
> ## Environment
> 
> - **Compiler Version:** go version go1.22.2 linux/amd64
> - **Distro Version:** Ubuntu 24.04.1 LTS
> 
> - **Additional Environment Details:**
>   - `[github.com/consensys/gnark](http://github.com/consensys/gnark) v0.11.0`
>   - `[github.com/consensys/gnark-crypto](http://github.com/consensys/gnark-crypto) v0.14.1-0.20240909142611-e6b99e74cec1`
> 
> ## Steps to Reproduce
> 
> You can download the needed files here: https://drive.google.com/drive/folders/1KQ5I3vv4bUllvqbatGappwbAkIcR2NI_?usp=sharing
> 
> You have to run
> 
> ```shell
> go run gnark_poc.go
> ```
> 
> in a terminal.
> 
> Running the provided code will result in a memory crash or an extremely large memory allocation, which can be observed using the following command:
> 

_Trimmed to 38 lines — full report: https://github.com/Consensys/gnark/security/advisories/GHSA-cph5-3pgr-c82g_
