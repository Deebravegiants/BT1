# [C] CVE-2025-65548

## Summary
Severity: Critical
Advisory: CVE-2025-65548
Aliases: PYSEC-2025-89
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2025-12-08
Source: https://osv.dev/vulnerability/CVE-2025-65548
Type: osv

## Details
NUT-14 allows cashu tokens to be created with a preimage hash. However, nutshell (cashubtc/nuts) before 0.18.0 do not validate the size of preimage when the token is spent. The preimage is stored by the mint and attacker can exploit this vulnerability to fill the mint's db nd disk with arbitrary data.

## References
- https://bitcointalk.org/index.php?topic=5564329
- https://delvingbitcoin.org/t/public-disclosure-denial-of-service-using-htlc-in-cashu/2090
- https://github.com/cashubtc/nuts/blob/main/07.md
- https://github.com/cashubtc/nuts/blob/main/14.md
- https://github.com/jamesob/delving-bitcoin-archive/blob/master/archive/rendered-topics/2025-11-November/2025-11-02-public-disclosure-denial-of-service-using-htlc-in-cashu-id2090.md
- https://preimage007.github.io/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/65xxx/CVE-2025-65548.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-65548
