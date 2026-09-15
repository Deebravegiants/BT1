# [H] CVE-2018-10831

## Summary
Severity: High
Advisory: CVE-2018-10831
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2018-05-09
Source: https://osv.dev/vulnerability/CVE-2018-10831
Type: osv

## Details
Z-NOMP before 2018-04-05 has an incorrect Equihash solution verifier that allows attackers to spoof mining shares, as demonstrated by providing a solution with {x1=1,x2=1,x3=1,...,x512=1} to bypass this verifier for any blockheader. This originally affected (for example) the Bitcoin Gold and Zcash cryptocurrencies, and continued to be exploited in the wild in May 2018 against smaller cryptocurrencies.

## References
- https://blog.zencash.com/update-for-the-equihash-mining-application-z-nomp/
- https://github.com/edwardz246003/misc/blob/master/Attackers%20Fake%20Computational%20Power%20to%20Steal%20Cryptocurrencies%20from%20Mining%20Pools.md
