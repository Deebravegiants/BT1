# [?] Differentiate sustained vs. bounded full-node DoS in vulnerability rubric

## Summary
Severity: Unknown
Chain: Zcash
Component: zcash/zcash
Published: 2026-05-21
Source: https://github.com/zcash/zcash/commit/9e93c94dbbb0ffe1d32586acab4739b0f00b8b27
Type: security-commit

## Details
Differentiate sustained vs. bounded full-node DoS in vulnerability rubric

The single "DoS vulnerabilities affecting full node or light client server
software" High-severity bullet conflates findings that enable sustained
service denial or bypass existing peer-management protections (genuinely
High) with bounded validation-ordering or wasted-work amplifiers that are
capped by existing `Misbehaving`-based banning. Tighten the High bullet
to require sustained, unbounded, or mitigation-bypassing impact, and add
a Low bullet to cover bounded amplifiers.

Bounded amplifiers are placed in Low rather than Moderate because
Moderate is reserved for individual user loss of funds (financial harm),
whereas bounded amplifiers cause only temporary, capped resource
consumption with no permanent harm — closer in practical impact to the
existing "individual user wallet DoS" Low bullet than to fund loss.
Placing them in Moderate would imply they are more severe than wallet
DoS, which does not track: a wallet DoS that temporarily locks out a
user's funds is at least as impactful to that user as a bounded
node-CPU drain is to a node operator. The resulting structure cleanly
separates the rubric into "financial harm" (Moderate) and "bounded
nuisance" (Low) tiers.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
(cherry picked from commit 0a07b225719bd75212f66167319909ea57411d41)
