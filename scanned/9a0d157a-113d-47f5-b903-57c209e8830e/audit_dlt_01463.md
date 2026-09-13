# [?] graph/db/models: fix race condition in Node.PubKey

## Summary
Severity: Unknown
Chain: Bitcoin/Lightning
Component: lightningnetwork/lnd
Published: 2025-12-04
Source: https://github.com/lightningnetwork/lnd/commit/9906e61774816ab29b1755a3ab9e0f1036cab439
Type: security-commit

## Details
graph/db/models: fix race condition in Node.PubKey

The PubKey method had a race condition where concurrent calls could
all pass the nil check and race to write to the cached pubKey field.
This is a classic check-then-act race.

Remove the caching entirely to fix the race. The overhead of parsing
a public key is minimal and doesn't justify the added complexity and
race risk of caching.
