# [C] Deserialization of Untrusted Data in EthereumJ

## Summary
Severity: Critical
Chain: org.ethereum:ethereumj-core
Component: org.ethereum:ethereumj-core
CVE: CVE-2018-15890
CWE: Deserialization of Untrusted Data
Published: 2019-07-26
Source: https://github.com/advisories/GHSA-hf4p-jm7r-vjjj
Type: github-advisory

## Details
An issue was discovered in EthereumJ 1.8.2. There is Unsafe Deserialization in ois.readObject in mine/Ethash.java and decoder.readObject in crypto/ECKey.java. When a node syncs and mines a new block, arbitrary OS commands can be run on the server.
