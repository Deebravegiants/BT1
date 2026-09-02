### Title
Webhook `shop`, `topic`, and `webhook_id` fields are trusted without HMAC coverage, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC signable string from the raw request body only, while the `shop`, `topic`, `api_version`, and `webhook_id` values are read directly from unauthenticated HTTP headers and passed straight into the webhook handler. This breaks the identity binding `shop authenticated == shop acted upon`: the HMAC proves the *body* came from the holder of a valid signature, but it proves nothing about which shop, topic, or webhook the body belongs to.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

Meanwhile `shop`, `topic`, `api_version`, and `webhook_id` are pulled from headers that are never part of the signed material: [2](#0-1) 

`Registry.process` validates only the HMAC of the body and then forwards the header-derived `shop`/`topic`/`webhook_id` straight to the app's handler as trusted identity data: [3](#0-2) 

`HmacValidator.validate_signature` calls `verifiable_query.to_signable_string`, which for a webhook `Request` is just the raw body — the shop-domain header is never mixed into the signed digest: [4](#0-3) 

Because the HMAC only binds the body, any request with a valid `(body, hmac)` pair — obtainable by any merchant/tenant who legitimately receives webhooks from Shopify for their own shop (the HMAC is computed by Shopify using the app's secret and delivered to the recipient, not secret from the attacker's perspective) — can be replayed to the app's public webhook endpoint with an arbitrary `X-Shopify-Shop-Domain`/`X-Shopify-Topic`/`X-Shopify-Webhook-Id` header. The library's own validation logic has no way to detect this, since it never checks that the claimed shop/topic corresponds to what was actually signed.

This is exactly the "field acted on but not covered by the HMAC" identity-binding break: the equality that should hold is `shop_hmac_signed == shop_trusted_by_handler`, but the gem lets `shop_trusted_by_handler` be attacker-supplied while `shop_hmac_signed` doesn't exist at all.

### Impact Explanation
An app built on this gem that keys any tenant-scoped action (e.g., updating/deleting shop data, revoking access, processing `app/uninstalled` or `customers/data_request`) off `WebhookMetadata#shop` can be tricked into performing that action against a victim shop's tenant record while the attacker only supplies a body+HMAC pair legitimately issued for their own shop. This is cross-tenant access/action achieved without knowledge of the app's `client_secret`, satisfying the Critical severity bar (cross-tenant access) defined by the rules.

### Likelihood Explanation
Requires only that the attacker control one shop that has this app installed and receives at least one legitimate webhook (routine, not privileged), then replay that exact raw body + HMAC to the app's public webhook URL with forged Shopify headers. No secrets, tokens, or elevated access are required — only observation of one's own inbound webhook traffic, which any installing merchant can do.

### Recommendation
Bind the identity fields into the signed material, or otherwise cryptographically tie `shop`/`topic`/`webhook_id` to the verified body (e.g., require the host application to independently confirm the `shop` header against a known/registered shop associated with the specific webhook subscription id, or extend `to_signable_string` to include the header values Shopify actually signs). At minimum, document prominently that `Request#shop`/`#topic`/`#webhook_id` are NOT covered by `HmacValidator.validate` and must not be trusted for authorization decisions without additional verification.

### Proof of Concept
1. Attacker installs the target app on their own shop `attacker.myshopify.com` and receives a legitimate webhook, e.g. `orders/updated`, with body `B` and header `X-Shopify-Hmac-Sha256: H` (valid HMAC of `B` under the app's secret).
2. Attacker POSTs to the app's public webhook endpoint with the same body `B` and header `H`, but sets `X-Shopify-Shop-Domain: victim.myshopify.com` and any desired `X-Shopify-Topic`/`X-Shopify-Webhook-Id`.
3. `ShopifyAPI::Webhooks::Request.new` accepts the forged headers (only checks presence, not authenticity) — see `lib/shopify_api/webhooks/request.rb:45-63`.
4. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only hashes `@raw_body` — `lib/shopify_api/webhooks/registry.rb:188-190`, `lib/shopify_api/utils/hmac_validator.rb:26-31`.
5. The handler receives `WebhookMetadata` with `shop: "victim.myshopify.com"` and performs its tenant-scoped logic against the victim shop using attacker-controlled body content.

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
