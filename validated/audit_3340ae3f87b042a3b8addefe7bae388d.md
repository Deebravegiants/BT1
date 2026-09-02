### Title
Webhook `shop`, `topic`, `api_version`, and `webhook_id` Identity Fields Are Not Covered by HMAC Verification, Enabling Shop-Domain Spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` derives the tenant identity (`shop`) and other metadata that is handed to the application's webhook handler entirely from HTTP headers, while the HMAC signature that `Utils::HmacValidator` verifies covers only the raw request body. This breaks the binding `shop_used_by_handler == shop_that_produced_the_hmac`, allowing an attacker who controls any shop that can legitimately trigger a webhook (an "unprivileged" tenant of the same multi-tenant app) to replay a validly-HMAC'd body while forging the `X-Shopify-Shop-Domain` header to impersonate a different shop.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

The `shop`, `topic`, `api_version`, and `webhook_id` accessors are all read straight from unauthenticated HTTP headers: [2](#0-1) 

`Utils::HmacValidator.validate` computes and compares the HMAC only against `verifiable_query.to_signable_string` (i.e., the raw body), never incorporating the headers: [3](#0-2) 

`Registry.process` checks the HMAC and, on success, immediately trusts `request.shop` as the tenant identity that gets forwarded to the host application's handler: [4](#0-3) 

Because the HMAC is computed with the app's shared `client_secret`/`api_secret_key` over the body only, any request bearing a body+HMAC pair that was legitimately generated for shop A will pass `HmacValidator.validate` regardless of what `X-Shopify-Shop-Domain` header is sent. An attacker who operates their own shop (or has access to any single shop's legitimate webhook deliveries, e.g. via a public app install) can capture one genuine `(raw_body, hmac)` pair from their own shop's webhook and replay it to the app's webhook endpoint with the `X-Shopify-Shop-Domain` header rewritten to a victim shop domain. The signature still validates (it never covered the header), so `Registry.process` calls the handler with `WebhookMetadata.new(shop: request.shop, ...)` carrying the attacker-chosen shop value alongside body content that was never actually sent by that shop.

This is the same root-cause class as the reported bug: a value that is *acted upon* (the shop tenant binding, analogous to Aave's `ltv`/liquidation-threshold field) is not checked/covered against the authenticated envelope (the HMAC "data" field), letting an attacker corrupt a downstream, security-relevant identity field while the check that is supposed to gate trust (`HmacValidator.validate`) reports success.

### Impact Explanation
If the host application uses `WebhookMetadata#shop` (as delivered by this gem) to key session/token lookups, dedupe events, apply shop-scoped mutations, or route data (a very common and encouraged pattern shown in `docs/usage/webhooks.md`), an attacker can make the app attribute attacker-controlled webhook content to an arbitrary victim shop domain while the request still carries a cryptographically valid signature from the gem's point of view. This crosses the tenant boundary the HMAC is supposed to enforce (cross-tenant action under `Critical` in the given impact list), even though it requires the app to trust the gem's exposed `shop` field — which is exactly what the gem's own API/docs tell integrators to do.

### Likelihood Explanation
Exploitation only requires: (1) the ability to receive one legitimate webhook delivery from any shop that has the app installed (trivial for a public/embedded app — the attacker installs the app on their own store), and (2) the ability to POST to the app's public webhook endpoint with a forged `X-Shopify-Shop-Domain` (or `shopify-shop-domain`) header — no access to `api_secret_key`, tokens, or TLS interception is needed. This is a purely unprivileged-internet-user attack against the gem's exposed verification primitive.

### Recommendation
Include the identity-bearing headers (`shop-domain`, `topic`, `api-version`, `webhook-id`) in the signable string that `HmacValidator` verifies, or otherwise cryptographically bind them to the payload before exposing them via `WebhookMetadata`. At minimum, `Request#to_signable_string` should not diverge from the fields the host application is expected to trust (`shop`, `topic`, etc.) — either sign a canonical representation containing all of them, or document loudly (and enforce in-library) that `shop` must never be used as a tenant/session key without independent verification.

### Proof of Concept
1. Attacker installs the target app on their own shop `attacker.myshopify.com` and triggers any subscribed webhook topic, capturing the raw POST body `B` and the `X-Shopify-Hmac-Sha256` header `H` that Shopify sent (valid because Shopify itself signs it with the app's shared secret against `B`).
2. Attacker replays a new HTTP request to the app's webhook endpoint with:
   - Body = `B` (unchanged)
   - `X-Shopify-Hmac-Sha256` = `H` (unchanged)
   - `X-Shopify-Topic` = unchanged or arbitrary
   - `X-Shopify-Shop-Domain` = `victim.myshopify.com` (forged)
3. `ShopifyAPI::Webhooks::Request.new` builds a request whose `to_signable_string` is still `B`; `Utils::HmacValidator.validate` recomputes HMAC over `B` and it matches `H`, so validation succeeds (`lib/shopify_api/utils/hmac_validator.rb:26-31`).
4. `Registry.process` proceeds and calls the app's handler with `WebhookMetadata.new(shop: "victim.myshopify.com", body: parsed(B), ...)` (`lib/shopify_api/webhooks/registry.rb:198-199`), even though `victim.myshopify.com` never sent this webhook — the shop field is fully attacker-controlled despite HMAC "verification" having passed.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L16-33)
```ruby
      def topic
        T.cast(shopify_header("topic"), String)
      end

      sig { returns(String) }
      def shop
        T.cast(shopify_header("shop-domain"), String)
      end

      sig { returns(String) }
      def api_version
        T.cast(shopify_header("api-version"), String)
      end

      sig { returns(String) }
      def webhook_id
        T.cast(shopify_header("webhook-id"), String)
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
