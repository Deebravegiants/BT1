Confirmed the root cause. The finding is solid.

### Title
Webhook shop/topic attribution not covered by HMAC signature enables cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw HTTP body, so the HMAC-SHA256 signature verified by `ShopifyAPI::Utils::HmacValidator.validate` binds *only* the payload bytes to the app's `api_secret_key`. The `shop` and `topic` values that `ShopifyAPI::Webhooks::Registry.process` uses to attribute and dispatch the webhook are read straight from HTTP headers that are never covered by that signature, so an authenticated-payload / unauthenticated-header mismatch lets a request with a legitimately-signed body be replayed with an arbitrary shop or topic.

### Finding Description
`Request#to_signable_string` is defined as: [1](#0-0) 

which returns only `@raw_body`, while `shop` and `topic` are pulled from separate, unsigned headers: [2](#0-1) 

`HmacValidator.validate` computes the signature strictly from `to_signable_string`: [3](#0-2) 

`Registry.process` accepts the request once this body-only signature checks out, then dispatches using the unauthenticated `shop`/`topic` header values: [4](#0-3) 

Because a single app's `api_secret_key` is shared across every shop that has installed the app (it is not per-shop), any merchant who has installed the app can legitimately trigger a real webhook on their own store, capture the resulting genuinely-signed request from Shopify (valid HMAC over the body), and then resend that exact body to the app's public webhook endpoint while substituting the `X-Shopify-Shop-Domain` (and/or `X-Shopify-Topic`) header for a different, victim shop/topic. `HmacValidator.validate` still returns `true` because the signed bytes (the body) are unchanged, and `Registry.process` will hand the handler a `WebhookMetadata` whose `shop` is the attacker-chosen victim domain — breaking the equality "shop the HMAC authenticates" == "shop the application acts on."

### Impact Explanation
This breaks tenant isolation: a webhook handler that trusts `WebhookMetadata#shop` to scope data writes/reads (a common and encouraged usage pattern for multi-tenant Shopify apps) can be made to process attacker-controlled payload content under a victim shop's identity, or be misrouted to a handler for a different topic than actually occurred. This is a cross-tenant data-integrity/access issue reachable by any regular (non-privileged) merchant who has installed the app — no `api_secret_key`, access/refresh token, or victim credentials are required.

### Likelihood Explanation
Exploitation requires only: (1) installing the app as an ordinary merchant (a normal, unprivileged action for any app with public/open installs), (2) triggering a real store event to obtain one genuinely HMAC-signed webhook body from Shopify, and (3) POSTing that captured body to the app's public webhook endpoint with a modified shop/topic header, which is trivial to script. No secret material needs to be recovered or brute-forced.

### Recommendation
Bind the shop/topic identity into the verified signature domain rather than trusting bare headers: e.g., include `shop` (and `topic`) in the bytes that are HMAC-verified, or independently corroborate the header-supplied shop against a value obtained from a trusted, already-authenticated channel (such as the offline session/access token record for that shop) before dispatching, and reject requests where the two disagree.

### Proof of Concept
1. Install the target app on shop `attacker.myshopify.com`.
2. Trigger any subscribed event (e.g., create an order) so Shopify sends a legitimately signed webhook: headers include `X-Shopify-Hmac-Sha256: <valid signature over BODY>`, `X-Shopify-Shop-Domain: attacker.myshopify.com`, `X-Shopify-Topic: orders/create`.
3. Capture the raw request (`BODY`, valid HMAC).
4. Resend the identical `BODY` and HMAC header to the app's public webhook endpoint, but replace `X-Shopify-Shop-Domain` with `victim.myshopify.com`.
5. `ShopifyAPI::Webhooks::Request.new(raw_body: BODY, headers: forged_headers)` + `ShopifyAPI::Webhooks::Registry.process(request)` passes `HmacValidator.validate` (since it only checks `BODY`) and invokes the handler with `WebhookMetadata.new(shop: "victim.myshopify.com", ...)`, causing the app to act on attacker-supplied data as though it came from the victim shop.

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
