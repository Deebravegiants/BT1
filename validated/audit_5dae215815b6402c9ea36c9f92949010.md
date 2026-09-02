### Title
Webhook `shop-domain` header is not covered by HMAC verification, allowing shop-identity spoofing on webhook delivery - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable content from the raw request body only, while `shop`, `topic`, `webhook_id`, and `api_version` are read directly from unauthenticated HTTP headers. `Utils::HmacValidator.validate` (used by `Webhooks::Registry.process`) only proves that the *body bytes* were signed with the app's secret — it proves nothing about which shop the request is asserted to originate from. An attacker who possesses one validly-signed webhook body (e.g. from a shop they legitimately installed the app on) can resubmit that exact body/HMAC pair to the app's public webhook endpoint while substituting an arbitrary `x-shopify-shop-domain` header, and the library will report the request as valid and attribute it to the spoofed shop.

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

The `shop`, `topic`, and `webhook_id` accessors are parsed straight from request headers with no cryptographic binding: [2](#0-1) 

`Registry.process` verifies only `Utils::HmacValidator.validate(request)` — i.e., the signature over the raw body — before dispatching the handler with `request.shop` as the tenant identifier: [3](#0-2) 

`HmacValidator.validate_signature` confirms only that `to_signable_string` (the raw body) matches the HMAC, never that `shop`/`topic` are part of what was signed: [4](#0-3) 

The identity binding broken is: `shop asserted in header` ≠ `shop covered by HMAC(secret, bytes)`. The library validates "bytes verified" (raw body signed by secret) but treats "bytes parsed" (shop/topic headers) as trustworthy without that binding — exactly the pattern called out in the analog class ("bytes verified versus bytes parsed").

Because the webhook endpoint is a public HTTP endpoint that must accept unauthenticated POSTs from the internet (that's how Shopify delivers webhooks), any actor who can obtain one legitimately-signed `(body, hmac)` pair — trivially available to any merchant who installs the app on their own store and receives a real webhook — can replay that exact pair to the same endpoint with a different `x-shopify-shop-domain` (or `shopify-shop-domain`) header value. `HmacValidator.validate` still returns `true` because the signature check never inspects the header. `Registry.process` then calls the handler with `WebhookMetadata` carrying the attacker-chosen `shop`, letting the attacker inject data that is processed as if it belongs to a shop they do not control.

### Impact Explanation
If the host application uses `WebhookMetadata#shop` (as documented/intended, see `handler.handle(data: WebhookMetadata.new(topic: ..., shop: request.shop, body: ..., ...))`) to select which tenant's state to update, this enables cross-tenant data injection: an attacker-controlled payload from their own shop's legitimate webhook can be attributed to and processed against a victim shop's record, without ever needing the victim's credentials, access token, or the app's `client_secret`. This matches the "cross-tenant access" Critical impact category defined for this scan.

### Likelihood Explanation
Likelihood is high in practice: obtaining one signed webhook is as easy as installing the target app on any store the attacker controls (a normal, unprivileged action) and capturing the raw POST that Shopify sends to the app's registered endpoint. Replaying it with a modified shop header requires no secret material and no bypass of TLS.

### Recommendation
Bind the tenant/shop identity into what is verified, not just the raw body:
- Include the `shop-domain` (and ideally `topic`, `webhook-id`) header values in the signable string used for HMAC verification, or
- After HMAC validation, independently verify that `request.shop` corresponds to a shop with a known, stored session/installation for this app before trusting it as the processing tenant, rejecting webhooks for shops the app cannot corroborate.

### Proof of Concept
1. Install the app (or otherwise trigger a webhook) on attacker-owned shop `attacker.myshopify.com`; capture the raw POST body `B` and its `x-shopify-hmac-sha256` header `H` sent by Shopify to the app's public webhook endpoint.
2. Replay the request to the same endpoint, keeping body `B` and header `H` unchanged, but set `x-shopify-shop-domain: victim.myshopify.com`.
3. `Utils::HmacValidator.validate` in `lib/shopify_api/utils/hmac_validator.rb:26-31` succeeds because it only checks `HMAC(secret, B) == H`.
4. `Registry.process` (`lib/shopify_api/webhooks/registry.rb:188-200`) dispatches the handler with `shop: "victim.myshopify.com"`, causing the app to process attacker-controlled body content under the victim shop's tenant context.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-23)
```ruby
      sig { returns(String) }
      def topic
        T.cast(shopify_header("topic"), String)
      end

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
