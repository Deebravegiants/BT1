### Title
Webhook `shop-domain` header used for tenant identification is not covered by the HMAC signature - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates a webhook solely by validating the HMAC over the raw request body, but the `shop` value that is subsequently handed to the app's webhook handler is read from an HTTP header that is never included in the signed material. This breaks the binding "shop authenticated == shop acted on."

### Finding Description
`ShopifyAPI::Utils::HmacValidator.validate` computes the signature from `verifiable_query.to_signable_string` and compares it against the received HMAC: [1](#0-0) 

For webhook requests, `to_signable_string` returns only the raw JSON body — it deliberately excludes any headers: [2](#0-1) 

Meanwhile `shop` is read directly from the `x-shopify-shop-domain` / `shopify-shop-domain` HTTP header, which is completely outside the HMAC's coverage: [3](#0-2) 

`Registry.process` validates only the HMAC (i.e., only the body) and then dispatches to the topic handler using `request.shop` as the tenant identifier, with no separate check binding shop to the signed content: [4](#0-3) 

Because the app's `client_secret` (and thus the HMAC key) is the same across every shop installation of the app, any two webhook deliveries for the same app — regardless of which shop triggered them — are signed with the identical secret. An entity that legitimately receives a correctly-signed webhook for shop A (e.g., a merchant who owns/operates shop A and can capture its own webhook traffic, or any party that can observe/replay a delivery to the app's public endpoint) can resend the same `(raw_body, hmac)` pair while substituting the `x-shopify-shop-domain` header value with shop B's domain. `HmacValidator.validate` will still succeed (it never looks at the header), and `Registry.process` will invoke the handler with `WebhookMetadata.new(... shop: request.shop ...)` reporting shop B, even though the payload/body was never actually produced for shop B.

This is exactly the "field acted on but not covered by the HMAC" bypass class: the identity binding `shop_authenticated == shop_used_for_tenant_dispatch` does not hold, because only the body is authenticated while `shop` is trusted from an unauthenticated header.

### Impact Explanation
If the host application uses `data.shop` from the webhook handler to look up/select a merchant session, write to per-tenant storage, or otherwise scope an operation to a specific store (which is the documented purpose of `WebhookMetadata#shop`), an attacker who can obtain one validly-signed webhook body for the app (from their own shop or by intercepting/replaying a delivery) can cause that body to be attributed to a different, victim shop. This is a cross-tenant data/attribution confusion: the app processes attacker-supplied body content while believing it came from the victim's store, which can lead to cross-tenant data corruption or unauthorized actions performed "as" another merchant's webhook.

### Likelihood Explanation
The attacker only needs one legitimately-signed webhook body from any shop using the target app (trivial to obtain by installing/using the app on their own store, since a merchant naturally receives HMAC-valid webhooks for their own actions) and the ability to POST to the app's public webhook endpoint with a modified `shop-domain` header — no access token, `client_secret`, or privileged account is required. This satisfies the "unprivileged internet user" bar.

### Recommendation
Include the `shop` (and ideally `topic`, `api_version`, `webhook_id`) values in the signable material used for HMAC verification, or perform a secondary authenticated binding — e.g., verify the `shop-domain` header against an expected/allow-listed shop tied to the session/installation context before dispatching to the handler — rather than trusting it purely because the body's HMAC checks out.

### Proof of Concept
1. App is installed on attacker-owned shop `attacker.myshopify.com`. Attacker triggers a webhook (e.g., `orders/create`) and captures the resulting POST: raw body `B` and header `x-shopify-hmac-sha256: H` (valid because `H = HMAC(client_secret, B)`).
2. Attacker resends the exact same request to the app's webhook endpoint, but replaces `x-shopify-shop-domain: attacker.myshopify.com` with `x-shopify-shop-domain: victim.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` parses the header (no HMAC check yet), and `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes `HMAC(client_secret, B)` and it matches `H` — validation succeeds because `B` and `H` are unchanged.
4. `Registry.process` invokes the registered handler with `WebhookMetadata.new(shop: "victim.myshopify.com", body: parsed(B), ...)`, so the app believes attacker-controlled body content originated from `victim.myshopify.com`. [4](#0-3) [2](#0-1)

### Citations

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```

**File:** lib/shopify_api/webhooks/request.rb (L20-23)
```ruby
      sig { returns(String) }
      def shop
        T.cast(shopify_header("shop-domain"), String)
      end
```

**File:** lib/shopify_api/webhooks/request.rb (L35-43)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end

      sig { returns(T::Hash[String, T.untyped]) }
      def parsed_body
        JSON.parse(@raw_body)
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
