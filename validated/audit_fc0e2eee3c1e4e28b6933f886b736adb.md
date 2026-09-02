Line 125 in `docs/usage/webhooks.md` explicitly promises that `Registry.process` "will verify the request did indeed come from Shopify," documenting the exact identity binding the gem claims to enforce. That claim is broken because the HMAC covers only the raw body.

### Title
Webhook `shop`, `topic`, and `webhook_id` headers are not covered by HMAC verification, enabling cross-tenant webhook forgery - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` is documented to "verify the request did indeed come from Shopify" before invoking the app's handler, but the HMAC signature it checks only binds the raw request body — not the `shop-domain`, `topic`, `webhook-id`, or `api-version` headers that are passed straight through to the handler as trusted, shop-scoped data.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`ShopifyAPI::Utils::HmacValidator.validate` computes the HMAC exclusively over `to_signable_string`: [2](#0-1) 

`Registry.process` treats a successful HMAC check as proof the entire request "did indeed come from Shopify" (per `docs/usage/webhooks.md:125`) and then dispatches `request.shop`, `request.topic`, and `request.webhook_id` — all read from unauthenticated headers — into `WebhookMetadata` handed to the app's handler: [3](#0-2) 

`shop`, `topic`, and `webhook_id` are simple header reads with no cryptographic binding to the signed body: [4](#0-3) 

The broken identity binding, as an equality that should hold but doesn't:
`HMAC(api_secret_key, raw_body)` is valid ⇏ `shop header == shop that legitimately produced raw_body`.

Since a merchant's app secret is shared across every shop that installs the app, any unprivileged user can install the target public app on their own store (an ordinary, unprivileged action) and receive a genuine Shopify webhook — body plus a correctly computed HMAC — for events on their own shop. Because the `shop-domain`, `topic`, and `webhook-id` headers are excluded from the signed content, the attacker can replay that exact body/HMAC pair to the app's public webhook endpoint while substituting the `shop-domain` header for any other merchant on the platform (and/or the `topic` header for any topic the app has registered). `Registry.process` will pass HMAC verification and hand the handler a `WebhookMetadata` claiming the forged shop and topic, even though the body content actually originated from the attacker's own shop.

### Impact Explanation
This crosses a tenant boundary: an attacker with no relationship to a victim shop can make the target app process arbitrary, attacker-crafted webhook payloads *attributed to that victim shop*. Depending on how the host app's handler uses `data.shop` (e.g., to look up the merchant's session/store record and update local state, inventory, order records, GDPR redaction flags, etc.), this can lead to cross-tenant data corruption or spoofed events without ever needing the app's `api_secret_key`, an access token, or any privileged credential — satisfying the Critical "cross-tenant access" bar.

### Likelihood Explanation
Any user can install a public app on their own store without special privilege, giving them a steady stream of validly-HMAC'd (body, signature) pairs for topics the app subscribes to. Replaying such a pair to the app's public webhook URL with a modified `shop-domain`/`topic` header requires only basic HTTP tooling; no interception of Shopify's traffic or knowledge of the secret is needed.

### Recommendation
Bind the identity headers into the signed material, or otherwise ensure `shop`, `topic`, and `webhook_id` are authenticated together with the body:
- At minimum, `Registry.process` should cross-check the incoming `shop` header against the shop for which the requesting app instance actually expects a webhook (e.g., an installed/active session lookup) before invoking the handler, rather than trusting the header outright once HMAC-on-body passes.
- Update `docs/usage/webhooks.md` to accurately describe that only the body is authenticated by HMAC, and that host apps must independently authenticate `shop` if they use it for tenant-scoped effects — but this documentation-only fix does not close the gap that `Registry.process` currently promises full request authenticity.

### Proof of Concept
1. Attacker installs a public target app on their own store `attacker.myshopify.com`, registering for topic `orders/create`.
2. Shopify sends a webhook to the attacker's registered callback URL with a valid `x-shopify-hmac-sha256` header computed over the JSON body using the app's real `api_secret_key`.
3. Attacker captures the raw body and the `hmac-sha256` header unchanged, then issues a new HTTP POST to the same app's webhook endpoint with:
   - identical body and `x-shopify-hmac-sha256` header,
   - `x-shopify-shop-domain: victim-shop.myshopify.com`,
   - optionally a different `x-shopify-topic`/`x-shopify-webhook-id` matching another registered handler.
4. `ShopifyAPI::Webhooks::Request.new` accepts it (headers merely need to be present, per `lib/shopify_api/webhooks/request.rb:45-63`), and `Registry.process` calls `Utils::HmacValidator.validate(request)` which succeeds because it only checks the body/hmac pair: [5](#0-4) 
5. The app's handler receives `WebhookMetadata` with `shop: "victim-shop.myshopify.com"` and processes it as if the victim shop actually triggered this event.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-33)
```ruby
      sig { returns(String) }
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
