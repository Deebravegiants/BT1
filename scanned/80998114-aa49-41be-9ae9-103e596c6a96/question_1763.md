# Q1763: to_signable_string — no single-use via array-style parameters

## Question
Is there a reachable state in which an unprivileged attacker, controlling `shop[]=` / `state[]=` style keys that a Rack parse turns into arrays before they reach `AuthQuery.new` at `AuthQuery#to_signable_string`, the only bytes `HmacValidator` ever sees for an OAuth callback, makes `AuthQuery#to_signable_string` return a result the caller treats as authenticated, given that nothing marks a signed callback as consumed? Test SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host and quantify Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/auth/oauth/auth_query.rb` -> `AuthQuery#to_signable_string`
- Entrypoint: `AuthQuery#to_signable_string`, the only bytes `HmacValidator` ever sees for an OAuth callback
- Attacker controls: `shop[]=` / `state[]=` style keys that a Rack parse turns into arrays before they reach `AuthQuery.new`
- Exploit idea: nothing marks a signed callback as consumed
- Invariant to test: SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `to_signable_string` includes every field the callback route reads, by reflecting over the route's params
