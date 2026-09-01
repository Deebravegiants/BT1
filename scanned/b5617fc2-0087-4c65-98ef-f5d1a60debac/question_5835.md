# Q5835: create_instance — template selection is textual via attribute name with punctuation

## Question
Can a response key containing `-`, `?`, `!`, spaces or `@`, after `clean_key` rewriting, supplied by an unprivileged attacker at `create_instance(data:, session:, instance:)`, which builds objects from API response JSON via `public_send("#{attribute}=", ...)`, make `Rest::Base.create_instance` and the code consuming its result disagree, given that `get_path` picks a template by matching available ids, so a crafted `ids` hash selects a different template than intended? The binding to test is CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted; the impact to prove is High - scope or expiry check bypass granting an operation the session was never authorized for.

## Target
- File/function: `lib/shopify_api/rest/base.rb` -> `Rest::Base.create_instance`
- Entrypoint: `create_instance(data:, session:, instance:)`, which builds objects from API response JSON via `public_send("#{attribute}=", ...)`
- Attacker controls: a response key containing `-`, `?`, `!`, spaces or `@`, after `clean_key` rewriting
- Exploit idea: `get_path` picks a template by matching available ids, so a crafted `ids` hash selects a different template than intended
- Invariant to test: CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted
- Expected Immunefi impact: High - scope or expiry check bypass granting an operation the session was never authorized for (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest + WebMock: call a generated resource's `find` with an `ids` value containing `/` and assert the recorded request path
