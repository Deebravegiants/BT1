Based on my investigation, I have enough to finalize the analog.

### Title
Webhook `shop-domain` header is trusted for tenant routing but is not covered by the HMAC signature - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC signature only over the raw request body, while the `shop`, `topic`, `webhook_id`, and `api_version` values are read directly from unauthenticated HTTP headers. `ShopifyAPI::Webhooks::Registry.process` validates the HMAC and then forwards `request.shop` (and the other header-derived values) straight to the app's `WebhookHandler` as the authoritative tenant identity for the payload, without any cryptographic binding between the shop identity and the signed bytes.

### Finding Description
`Webhooks::Request` implements `Utils::VerifiableQuery`, and its `to_signable_string` returns only `@raw_body`: [1](#0-0) 

`shop`, however, is pulled from the `shopify-shop-domain` / `x-shopify-shop-domain` header, which is never mixed into the signable string: [2](#0-1) 

`HmacValidator.validate` only ever verifies `verifiable_query.to_signable_string` (the body) against the secret-derived signature — it has no notion of the shop header: [3](#0-2) 

`Registry.process` raises only if the body HMAC is invalid, then hands `request.shop` directly to the handler as the tenant identity for the event, with no cross-check that the body actually pertains to that shop: [4](#0-3) 

The broken equality is: `shop authenticated by the HMAC` (∅ — the signature covers only the body) vs. `shop used to route/attribute the webhook payload` (`request.shop`, taken from an attacker-controllable header). Before the attacker's request: a legitimate webhook for Shop A arrives with body `B`, `hmac = HMAC(secret, B)`, and header `shop-domain: A`. After the attacker's replay: the same body `B` and the same valid `hmac` are resent to the app's public webhook endpoint with `shop-domain: B` (a victim shop) substituted. `Registry.process` still finds `Utils::HmacValidator.validate` returns `true` (only `B`'s bytes are checked) and dispatches `WebhookMetadata.new(shop: "B", body: parsed_body, ...)` to the handler — the app now processes attacker-supplied body content as though it were an authentic event from a different tenant's shop.

### Impact Explanation
This breaks the tenant boundary the webhook subsystem is meant to enforce: any party capable of observing one genuine signed webhook delivery (e.g., an attacker who is themselves a merchant with the app installed, capturing traffic to their own endpoint) can resend that exact body/HMAC pair to the app's webhook endpoint while claiming an arbitrary `shop-domain`. Because the gem hands this header value to the app as the trusted shop identity for the payload once HMAC validation passes, downstream logic that keys off `WebhookMetadata#shop` (e.g. looking up which merchant's data to update/delete/redact) can be made to act on the wrong tenant's records — a cross-tenant confusion condition rooted entirely in this gem's verification design, not in any host-application misuse.

### Likelihood Explanation
Exploitation requires the attacker to have legitimately received at least one real webhook (trivial for any merchant who installs the app on their own shop, since webhook endpoints are public HTTP(S) URLs the app must expose) and to be able to POST directly to the app's webhook endpoint with custom headers, which is standard capability for any internet client. No secret material, TLS interception, or privileged account is needed.

### Recommendation
Bind the shop identity (and other routing metadata such as `topic`/`webhook_id`) into the signed material, or otherwise cryptographically tie `shop-domain` to the payload before trusting it — e.g. verify the header value against a shop identifier embedded in the payload body itself, or require callers to look up the destination shop from their own authenticated session/webhook-registration record rather than from `WebhookMetadata#shop`, and document this requirement clearly. At minimum, `Webhooks::Request`/`Registry` should not present the header-derived shop as if it had been authenticated by `HmacValidator.validate`.

### Proof of Concept
1. App installs webhook subscription; Shopify sends a legitimate webhook to the app for `shop-a.myshopify.com` with body `B` and header `X-Shopify-Hmac-Sha256: H = HMAC(secret, B)`.
2. Attacker (who owns `shop-a` and can observe this traffic, e.g. via a local proxy in their own dev environment) resends the exact same request to the app's public webhook endpoint but replaces `X-Shopify-Shop-Domain: shop-a.myshopify.com` with `X-Shopify-Shop-Domain: shop-victim.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: forged_headers)` builds successfully; `hmac` is still `H`, unaffected by the header change.
4. `ShopifyAPI::Webhooks::Registry.process(request)` calls `Utils::HmacValidator.validate(request)`, which recomputes `HMAC(secret, B) == H` — validation succeeds.
5. The registered handler receives `WebhookMetadata.new(shop: "shop-victim.myshopify.com", body: parsed(B), ...)`, i.e., attacker-controlled body content attributed to a shop the attacker does not own.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L20-43)
```ruby
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

      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end

      sig { returns(T::Hash[String, T.untyped]) }
      def parsed_body
        JSON.parse(@raw_body)
      end
```

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-31)
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

        private

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
