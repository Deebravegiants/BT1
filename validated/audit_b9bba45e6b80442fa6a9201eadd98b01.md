### Title
Webhook `shop`/`topic`/`webhook_id` headers are trusted without being covered by the HMAC signature - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` claims to "verify the request did indeed come from Shopify," but the HMAC verification only covers the raw request body. The `shop-domain`, `topic`, `webhook-id`, and `api-version` headers that are handed to the app's handler are never included in the signed content, so they are not bound to the authenticated payload.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Utils::HmacValidator.validate` computes/verifies the HMAC exclusively over `verifiable_query.to_signable_string`: [2](#0-1) 

`Registry.process` uses this same HMAC check to authorize the whole request, then forwards `request.shop`, `request.topic`, and `request.webhook_id` — all read directly from unauthenticated headers — straight to the app's handler: [3](#0-2) 

The `shop` accessor is a pure header read with no cross-check against the signed body: [4](#0-3) 

The documentation for `Registry.process` explicitly promises this "will verify the request did indeed come from Shopify," which is materially stronger than what the implementation delivers: [5](#0-4) 

The identity binding that is broken:
`HMAC-verified content == raw_body only`, while `data used to route/attribute the webhook (shop, topic, webhook_id) == unauthenticated header values`. These two sets are disjoint, so the "verified" property never actually extends to the shop attribution that host applications rely on to know which tenant a webhook belongs to.

### Impact Explanation
Shopify computes the webhook HMAC using the app's single `api_secret_key` (i.e. the app's client secret), which is identical across every merchant/shop that installs the app — it is not a per-shop secret. Consequently, a valid `(raw_body, hmac)` pair obtained from one shop's real webhook delivery remains cryptographically valid for that same body regardless of which shop the request claims to be from. Because the `x-shopify-shop-domain` header is not part of the signed content, an attacker who can reach the app's public webhook endpoint directly (bypassing Shopify's infrastructure — a plain HTTP POST) can replay a valid `(body, hmac)` pair while substituting an arbitrary victim shop's domain in the `shop-domain` header. `Registry.process` will accept it as HMAC-valid and pass the attacker-chosen `shop` to the handler as though it were verified. Any host application that uses `WebhookMetadata#shop` (via `Registry.process`'s call) to key which tenant's data to update — exactly as the library's own documentation instructs — can be tricked into cross-tenant data confusion/injection. This satisfies the "cross-tenant access" Critical impact category.

### Likelihood Explanation
The webhook processing pattern shown in this repo's own docs is copied verbatim by consuming apps, and merchants can trivially install the target app onto their own store to capture a legitimate `(body, hmac)` pair for a body they control, then replay it with a forged shop header directly against the app's HTTP endpoint (no Shopify infrastructure or secret material is required — only network access to the app's public webhook route). This is an unprivileged-internet-user-reachable path with no dependency on host-app misuse; the gem's documented contract ("will verify the request did indeed come from Shopify") is what is being violated.

### Recommendation
Bind the identity-relevant headers (`shop`, `topic`, `webhook_id`, `api_version`) into the signed content checked by `HmacValidator`, e.g., include them in `Request#to_signable_string` (matching how Shopify's own webhook signing scheme could be extended, or by independently verifying `shop` against the installed-shop registry before dispatching to a handler). At minimum, update `Registry.process` to cross-check that `request.shop` corresponds to a shop known to have an active session/installation for this app before invoking the handler, and correct the documentation to accurately describe what is and is not covered by the HMAC check.

### Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker.myshopify.com` and receives a legitimate webhook delivery with body `B` and header `x-shopify-hmac-sha256: H`, where `H = HMAC-SHA256(app_client_secret, B)`.
2. Attacker sends a raw HTTP POST directly to the victim app's public webhook endpoint (bypassing Shopify) with:
   - body: `B` (unchanged)
   - `x-shopify-hmac-sha256: H` (unchanged, still valid since it only signs `B`)
   - `x-shopify-shop-domain: victim-shop.myshopify.com` (forged)
   - `x-shopify-topic`, `x-shopify-webhook-id`: chosen by attacker
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because it only checks `HMAC(secret, B) == H` — headers are irrelevant to this check. [6](#0-5) 
4. The handler receives `WebhookMetadata.new(topic: ..., shop: "victim-shop.myshopify.com", body: parsed(B), ...)` and treats the forged `shop` value as authenticated, since the library asserted the request "did indeed come from Shopify." [7](#0-6)

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```

**File:** lib/shopify_api/webhooks/registry.rb (L188-199)
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
```

**File:** docs/usage/webhooks.md (L125-125)
```markdown
To process an http webhook, you need to listen on the route(s) you provided during the Webhook registration process, then when the route is hit construct a `ShopifyAPI::Webhooks::Request` and call `ShopifyAPI::Webhooks::Registry.process`. This will verify the request did indeed come from Shopify and then call the specified handler for that webhook. An example in Rails is shown below:
```
