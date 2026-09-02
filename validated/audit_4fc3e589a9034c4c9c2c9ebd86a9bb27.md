This confirms the vulnerability: the gem's own documentation explicitly states `ShopifyAPI::Webhooks::Registry.process` "will verify the request did indeed come from Shopify" (`docs/usage/webhooks.md:125`), and instructs consumers to trust `data.shop` (`docs/usage/webhooks.md:14,25-26`) — yet the `shop` field is derived from an unauthenticated header, never covered by the HMAC.

### Title
Webhook shop-domain header is not bound to the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw body [1](#0-0) , and `ShopifyAPI::Utils::HmacValidator.validate` computes/compares the HMAC solely over that signable string [2](#0-1) . Meanwhile `Request#shop` is read straight from the `shopify-shop-domain`/`x-shopify-shop-domain` HTTP header [3](#0-2) , which is not part of the signed material at all. `Registry.process` validates the HMAC and then hands `request.shop` directly to the merchant's handler as the tenant identity, with no additional check that the header matches the body/shop that was actually signed [4](#0-3) .

### Finding Description
This is the same bug class as the Solana vault issue: a field that downstream logic treats as authoritative (`allowed_token` / here, `shop`) is never checked against the value that was actually cryptographically verified (`deposit_token` / here, the HMAC-signed body). The binding that should hold is:

`request.shop (used to attribute the webhook to a tenant) == the shop that produced the HMAC-signed body`

but the code only enforces `HMAC(secret, raw_body) == received_signature`, with `shop` sourced from a header that is completely outside that computation. Since a single app typically shares one `api_secret_key` across all of its installed shops, anyone who legitimately receives real Shopify webhooks for their own shop (e.g., by installing the target app on a shop they control) possesses a fully valid `(raw_body, hmac)` pair signed with the app's secret. They can then replay that exact body/HMAC pair to the app's webhook endpoint while substituting an arbitrary `shopify-shop-domain` header value for a victim shop. `HmacValidator.validate` will pass because it never inspects headers [5](#0-4) , and `Registry.process` will invoke the app's handler with `WebhookMetadata` claiming the data belongs to the victim shop [6](#0-5) .

The gem's own docs promise that `process` "will verify the request did indeed come from Shopify" [7](#0-6)  and instruct handler authors to trust `data.shop` as "The shop domain of the webhook" [8](#0-7) . A host app that follows this documented contract has no way to detect the forged shop attribution — the gem gives it no signal that `shop` is unauthenticated.

### Impact Explanation
This breaks tenant isolation (cross-tenant access): an attacker who is a legitimate merchant of the app (or otherwise obtains one valid signed webhook body, e.g. via HTTP logs, a compromised low-trust endpoint, etc.) can inject arbitrary webhook payloads attributed to any other shop of their choosing. Depending on how the host app uses `data.shop` (e.g., looking up the victim's stored access token/session to act on their store, writing into the victim's tenant-scoped data, triggering GDPR/compliance webhook flows, or driving billing/plan logic), this can lead to cross-tenant data corruption or actions being taken against a shop the attacker does not control — satisfying the "cross-tenant access" Critical impact category.

### Likelihood Explanation
Likelihood is bounded by the fact that the attacker needs at least one genuine `(body, hmac)` pair signed with the app's `api_secret_key`. For public apps this is trivial to obtain: an attacker installs the app on their own store, which is enough to receive real HMAC-signed webhooks from Shopify for arbitrary topics/bodies they can influence (e.g., updating their own store's title, which is reflected in the body), then replays that body+signature with a spoofed `shop-domain` header targeting any other installed shop.

### Recommendation
Bind `shop` (and ideally `topic`/`webhook_id`) into the signed material, or otherwise cross-check the header against a value the app already trusts for that shop before dispatching to the handler:
- Include the `shop-domain`, `topic`, and `webhook-id` headers as part of `to_signable_string` (or a separate authenticated bundle) so `HmacValidator` verifies the full identity of the delivery, not just the JSON body.
- At minimum, document loudly (and ideally enforce in `Registry.process`) that `request.shop` is unauthenticated header data and that host apps must independently confirm it corresponds to a shop that legitimately installed the app before trusting it.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com`, causing Shopify to legitimately deliver a real webhook to the app's endpoint with a valid `x-shopify-hmac-sha256` for some body `B` (e.g., `orders/create` with attacker-controlled order data).
2. Attacker captures `(B, hmac(secret, B))` from that legitimate delivery (e.g., via their own reverse proxy/logs).
3. Attacker replays a request to the same webhook endpoint with the identical body `B` and `x-shopify-hmac-sha256`, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
4. `HmacValidator.validate` in `lib/shopify_api/utils/hmac_validator.rb` returns `true` because it only checks `B` against the HMAC. `Registry.process` in `lib/shopify_api/webhooks/registry.rb` dispatches to the handler with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: B, ...)`, causing the host app to process attacker-controlled data as if it belonged to the victim shop.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L20-23)
```ruby
      sig { returns(String) }
      def shop
        T.cast(shopify_header("shop-domain"), String)
      end
```

**File:** lib/shopify_api/webhooks/request.rb (L35-38)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end
```

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-22)
```ruby
        sig { params(verifiable_query: VerifiableQuery).returns(T::Boolean) }
        def validate(verifiable_query)
          return false unless verifiable_query.hmac

          result = validate_signature(verifiable_query, Context.api_secret_key)
          if result || Context.old_api_secret_key.nil? || T.must(Context.old_api_secret_key).empty?
            result
          else
            validate_signature(verifiable_query, T.must(Context.old_api_secret_key))
          end
        end
```

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```

**File:** lib/shopify_api/webhooks/registry.rb (L188-200)
```ruby
        sig { params(request: Request).void }
        def process(request)
          raise Errors::InvalidWebhookError, "Invalid webhook HMAC." unless Utils::HmacValidator.validate(request)

          handler = @registry[request.topic]&.handler

          unless handler
            raise Errors::NoWebhookHandler, "No webhook handler found for topic: #{request.topic}."
          end

          handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop,
            body: request.parsed_body, api_version: request.api_version, webhook_id: request.webhook_id))
        end
```

**File:** docs/usage/webhooks.md (L12-17)
```markdown
`data` will have the following keys
- `topic`, `String` - The topic of the webhook
- `shop`, `String` - The shop domain of the webhook
- `body`, `T::Hash[String, T.untyped]`- The body of the webhook
- `webhook_id`, `String` - The id of the webhook event to [avoid duplicates](https://shopify.dev/docs/apps/webhooks/best-practices#ignore-duplicates)
- `api_version`, `String` - The api version of the webhook
```

**File:** docs/usage/webhooks.md (L123-125)
```markdown
## Process a Webhook

To process an http webhook, you need to listen on the route(s) you provided during the Webhook registration process, then when the route is hit construct a `ShopifyAPI::Webhooks::Request` and call `ShopifyAPI::Webhooks::Registry.process`. This will verify the request did indeed come from Shopify and then call the specified handler for that webhook. An example in Rails is shown below:
```
