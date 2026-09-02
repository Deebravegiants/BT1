### Title
Webhook Shop-Domain Header Is Not Covered by HMAC Verification, Allowing Cross-Tenant Webhook Spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, while the `shop` (from the `shopify-shop-domain`/`x-shopify-shop-domain` header) that gets forwarded to the app's webhook handler is never included in the HMAC-signed material. `ShopifyAPI::Webhooks::Registry.process` validates the HMAC over the body only and then trusts the unauthenticated header value as the tenant identity passed to the handler.

### Finding Description
`Utils::HmacValidator.validate` recomputes an HMAC over `verifiable_query.to_signable_string` and compares it (via `OpenSSL.secure_compare`) to the `hmac` header value: [1](#0-0) 

For webhook requests, `to_signable_string` is defined as just the raw body: [2](#0-1) 

Meanwhile `shop` is read from a separate, unsigned header: [3](#0-2) 

`Registry.process` validates the HMAC and then constructs `WebhookMetadata` using `request.shop`, handing that value to the app's handler as the authoritative tenant identifier, without any check binding it to the signed content: [4](#0-3) 

This breaks the identity binding `bytes verified == bytes parsed`: the bytes cryptographically verified by the HMAC (the raw body) are not the same bytes used to determine the tenant (the `shop-domain` header). An unprivileged user who legitimately installs the app on their own shop receives genuinely-signed webhooks for that shop (signed with the app's real `api_secret_key`, which the attacker never needs to know). Because the header carrying `shop-domain` is excluded from the signed payload, that same attacker can resend the identical signed body to the app's webhook endpoint with the `x-shopify-shop-domain` header rewritten to a victim shop's domain. `HmacValidator.validate` still succeeds (it only checks the untouched body), so `Registry.process` calls the handler with `data.shop` set to the victim's domain and `data.body` equal to the attacker's own (attacker-controlled) webhook payload.

### Impact Explanation
This is a cross-tenant confusion at the library level: the gem hands the app a shop identity (`WebhookMetadata#shop`) that carries no cryptographic assurance of correctness, alongside a body that is genuinely signed but for a different context than the shop claimed. Any host application that uses `data.shop` from `ShopifyAPI::Webhooks::WebhookHandler#handle` as a trusted tenant key (exactly as the gem's own documentation instructs: `docs/usage/webhooks.md` shows `data.shop` used directly to key persistence/enqueue calls) will process attacker-supplied data under another merchant's identity — e.g., writing/overwriting per-shop state, redact/data-request handling, or business logic keyed by shop for a shop the attacker does not control. This matches the Critical "cross-tenant access" impact bucket, since the boundary crossed is the per-shop credential/data boundary that HMAC verification is meant to enforce.

### Likelihood Explanation
Likelihood is high for any app builder following the gem's documented pattern: no special privileges are required beyond installing the app on one's own store (an ordinary, unprivileged merchant action), capturing one legitimately-signed webhook delivery, and replaying it with a modified header to the app's own public webhook endpoint. No access token, `api_secret_key`, or leaked credential is needed.

### Recommendation
Include the tenant-identifying header (`shop-domain`) — along with `topic`, `webhook-id`, and `api-version` — in the signed material verified by `HmacValidator`, or otherwise cryptographically bind the shop value to the verified payload before it is exposed via `WebhookMetadata#shop`. At minimum, document prominently that `data.shop` is not authenticated by the HMAC check and must not be trusted as a tenant key without additional verification (e.g., cross-checking against a known/installed shop list).

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` and registers a webhook (e.g. `orders/create`).
2. Shopify delivers a webhook to the app's endpoint with a valid `x-shopify-hmac-sha256` computed over the raw body using the app's real `api_secret_key`, and header `x-shopify-shop-domain: attacker-shop.myshopify.com`.
3. Attacker captures this request (raw body + valid HMAC header) and resends it to the same endpoint, changing only `x-shopify-shop-domain` to `victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because `to_signable_string` returns only the (unmodified) raw body.
5. The app's handler is invoked with `data.shop == "victim-shop.myshopify.com"` and `data.body` equal to the attacker's crafted payload, as shown by the `WebhookMetadata` construction in `Registry.process`: [5](#0-4)

### Citations

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
