# [M] 5.3.2 Tokens With Multiple Addresses Can Be Stolen Due to Reliance onbalanceOf

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
**Severity:** Medium Risk

**Context:** AccountLib.sol#L

**Description:** Some ERC20 tokens have multiple valid contract addresses that serve as entrypoints for manipulat-
ing the same underlying storage (such as Synthetix tokens like SNX and sBTC and the TUSD stablecoin). Because
the FVM holds all tokens for all pools in the same contract, assumes that a contract address is a unique identifier
for a token, and relies on the return value ofbalanceOffor manipulated tokens to determine what transfers are
needed during transaction settlement, multiple entrypoint tokens are not safe to be used in pools.

For example, suppose there is a pool with non-zero liquidity where one token has a second valid address. An
attacker can atomically create a second pool using the alternate address, allocate liquidity, and then immediately
deallocate it. During execution of the_settlementfunction,getNetBalancewill return a positive net balance for
the double entrypoint token, crediting the attacker and transferring them the entire balance of the double entrypoint
token. This attack only costs gas, as the allocation and deallocation of non-double entrypoint tokens will cancel
out.

**Recommendation:** At a minimum, anyone interacting with contracts derived fromPortfolioVirtualshould be
explicitly warned not to create pools containing tokens with multiple valid addresses. An explicit blacklist could be
added to prevent any address other than an "official" one from being used to create pairs and pools for such tokens
(potentially fixed at deployment time, as double entrypoint tokens are rare and now widely known to be dangerous).
Architecturally, tokens could be stored in dedicated, special-purpose contracts for each token address, although
this would increase gas costs and complexity.

**Spearbit:** Marked as Acknowledged.
