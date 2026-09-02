Confirmed root cause: `ShopifyAPI::Webhooks::Registry.process` treats the request as authentic once `Utils::HmacValidator.validate(request)` passes, but that validator only checks the HMAC against `request.to_signable_string`, which for `Webhooks::Request` is `@raw_body` alone [1](#0-0) . The `shop` value that gets forwarded to the app's handler as the tenant identifier is read from the `shopify-shop-domain`/`x-shopify-shop-domain` header, which is never part of the signed bytes [2](#0-1) . `Registry.process` validates the HMAC and then blindly trusts `request.shop` when building `WebhookMetadata` for the handler [3](#0-2) .

### Title
Webhook shop-domain header is not covered by the HMAC, allowing cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating the HMAC over the raw body, then trusts the `shop` field read from an unsigned header to identify which tenant the event belongs to. Any party who can obtain one valid `(body, hmac)` pair signed with the app's `api_secret_key` — e.g., a merchant who installs the app on their own store and legitimately receives a webhook — can replay that same body/HMAC pair while substituting a different `x-shopify-shop-domain` (or `shopify-shop-domain`) header value, and the request will still pass validation. The handler is invoked believing the event originated from the victim shop named in the forged header.

### Finding Description
`Utils::HmacValidator.validate` computes and compares the HMAC using `verifiable_query.to_signable_string` [4](#0-3) . For `ShopifyAPI::Webhooks::Request`, `to_signable_string` returns only `@raw_body` [1](#0-0) , while `shop` (and `topic`, `webhook_id`, `api_version`) are pulled directly from HTTP headers with no cryptographic binding to the body [5](#0-4) .

`Registry.process` checks `Utils::HmacValidator.validate(request)` and, if it passes, immediately constructs `WebhookMetadata` using `request.shop` and dispatches it to the app's handler: `handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop, body: request.parsed_body, ...))` [3](#0-2) . There is no check that the signed body content actually corresponds to the shop asserted in the header — the equality that should hold (`shop used by the handler == shop the HMAC-signed bytes were generated for`) is never enforced.

Because many legitimate webhook topics use a fixed or attacker-predictable body (for example, `shop/redact`, `customers/redact`, `customers/data_request`, and `app/uninstalled` payloads carry the shop's own identifiers but the HMAC is computed over the *exact same secret* for every shop installing the app), an attacker who owns/operates their own Shopify store with the app installed can capture a real, validly-signed webhook delivery from Shopify for their own shop, then resend that exact body and HMAC to the app's webhook endpoint with the `shop-domain` header changed to a victim's `myshopify.com` domain. `Registry.process` will accept it as authentic for the victim tenant since `Utils::HmacValidator.validate` never inspects the `shop` header at all.

### Impact Explanation
This breaks the tenant-authentication boundary the HMAC is supposed to enforce: `shop asserted to the handler == shop the signed payload actually belongs to` no longer holds. Downstream apps that key session lookups, data mutation, or de-provisioning logic (e.g., app/uninstalled clearing a shop's stored access token, or GDPR redact handlers) off `WebhookMetadata#shop` can be tricked into performing tenant-scoped operations against a shop the attacker does not control — a cross-tenant access primitive stemming entirely from this gem's webhook verification helper.

### Likelihood Explanation
Requires no privileged credentials: any unprivileged internet user who can install the target app on a store they control (a normal, permitted action) can obtain a validly-HMAC'd webhook body/signature pair from Shopify and replay it against the app's public webhook endpoint with a forged shop header, since `api_secret_key` is shared across all shops for a given app and the header is completely outside the signed material.

### Recommendation
Include the shop domain (and topic/webhook id, if they must be trusted) inside the HMAC-signable material, or otherwise cryptographically bind `request.shop` to the verified payload before use. At minimum, `Webhooks::Request#to_signable_string` should not omit fields that are subsequently trusted for tenant identification by `Registry.process`/`WebhookMetadata`.

### Proof of Concept
1. Attacker installs the target Shopify app on their own dev/test store `attacker.myshopify.com` and registers a webhook topic whose delivered body is fixed/predictable (e.g., `app/uninstalled`, which Shopify sends with `{}` as the body, or any topic where the attacker fully controls the resource content of their own shop).
2. Shopify delivers a legitimate webhook to the app's endpoint with headers `x-shopify-shop-domain: attacker.myshopify.com`, `x-shopify-hmac-sha256: <valid HMAC over the body>`, and the raw body.
3. Attacker captures this request and resends it to the same endpoint, changing only `x-shopify-shop-domain` to `victim.myshopify.com` (or `shopify-shop-domain` for the new-format header), keeping the identical raw body and HMAC value.
4. `Utils::HmacValidator.validate` in `lib/shopify_api/utils/hmac_validator.rb` recomputes the HMAC over `@raw_body` only, which still matches, so `Registry.process` (`lib/shopify_api/webhooks/registry.rb`) proceeds and calls `handler.handle` with `WebhookMetadata(shop: "victim.myshopify.com", ...)`, causing the app to process the event as if it genuinely originated from the victim shop.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
