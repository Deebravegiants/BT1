# Q5679: get_path_ids — dynamic dispatch on response data via read-only attribute

## Question
Does `Rest::Base.get_path_ids` collapse two distinct identities into one when an unprivileged attacker submits an attribute listed in `read_only_attributes` presented in a payload that reaches `attributes_to_update` at `get_path_ids`, which enumerates the id placeholders a path template requires? Show that `public_send` and `instance_variable_set` targets are derived from data returned by the upstream call, not from a fixed allow-list, that CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted is violated, and that the consequence is High - scope or expiry check bypass granting an operation the session was never authorized for.

## Target
- File/function: `lib/shopify_api/rest/base.rb` -> `Rest::Base.get_path_ids`
- Entrypoint: `get_path_ids`, which enumerates the id placeholders a path template requires
- Attacker controls: an attribute listed in `read_only_attributes` presented in a payload that reaches `attributes_to_update`
- Exploit idea: `public_send` and `instance_variable_set` targets are derived from data returned by the upstream call, not from a fixed allow-list
- Invariant to test: CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted
- Expected Immunefi impact: High - scope or expiry check bypass granting an operation the session was never authorized for (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest + WebMock: call a generated resource's `find` with an `ids` value containing `/` and assert the recorded request path
