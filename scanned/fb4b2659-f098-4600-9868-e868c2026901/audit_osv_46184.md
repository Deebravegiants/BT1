# [M] JLSEC-2026-775

## Summary
Severity: Medium
Advisory: JLSEC-2026-775
Ecosystem: Julia
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N)
Published: 2026-07-20
Source: https://osv.dev/vulnerability/JLSEC-2026-775
Type: osv

## Affected
- Julia: `DuckDB_jll` — affected >=1.4.1+0 <1.4.2+0

## Details
DuckDB is a SQL database management system. DuckDB implemented block-based encryption of DB on the filesystem starting with DuckDB 1.4.0. There are a few issues related to this implementation. The DuckDB can fall back to an insecure random number generator (pcg32) to generate cryptographic keys or IVs. When clearing keys from memory, the compiler may remove the memset() and leave sensitive data on the heap. By modifying the database header, an attacker could downgrade the encryption mode from GCM to CTR to bypass integrity checks. There may be a failure to check return value on call to OpenSSL `rand_bytes()`. An attacker could use public IVs to compromise the internal state of RNG and determine the randomly generated key used to encrypt temporary files, get access to cryptographic keys if they have access to process memory (e.g. through memory leak),circumvent GCM integrity checks, and/or influence the OpenSSL random number generator and DuckDB would not be able to detect a failure of the generator. Version 1.4.2 has disabled the insecure random number generator by no longer using the fallback to write to or create databases. Instead, DuckDB will now attempt to install and load the OpenSSL implementation in the `httpfs` extension. DuckDB now uses secure MbedTLS primitive to clear memory as recommended and requires explicit specification of ciphers without integrity checks like CTR on `ATTACH`. Additionally, DuckDB now checks the return code.

## References
- https://duckdb.org/2025/09/16/announcing-duckdb-140.html
- https://github.com/duckdb/duckdb/blob/029a5b87ff5b1cd22f7f9717d48cd8830d00807c/src/common/random_engine.cpp#L20
- https://github.com/duckdb/duckdb/pull/17275
- https://github.com/duckdb/duckdb/security/advisories/GHSA-vmp8-hg63-v2hp
