# [H] Tendermint Client package vulnerable to Uncontrolled Resource Consumption

## Summary
Severity: High
Chain: github.com/tendermint/tendermint
Component: github.com/tendermint/tendermint
CVE: CVE-2019-25072
CWE: Uncontrolled Resource Consumption
Published: 2022-12-28
Source: https://github.com/advisories/GHSA-3fm3-m23v-5r46
Type: github-advisory

## Details
Due to support of Gzip compression in request bodies, as well as a lack of limiting response body sizes, a malicious server can cause a client to consume a significant amount of system resources, which may be used as a denial of service vector.
