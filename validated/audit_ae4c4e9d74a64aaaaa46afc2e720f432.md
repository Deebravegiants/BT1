### Title
Webhook Shop/Topic Identity Spoofing via HMAC Scope Mismatch - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable content from the raw HTTP body only, while the `shop`, `topic`, `webhook_id`, and `api_version` values used to route and attribute the webhook to a tenant are read directly from unauthenticated HTTP headers. `ShopifyAPI::Utils::HmacValidator` verifies only the bytes returned by `to_signable_string`, so anything outside that string — including the shop-domain header — is trusted without being covered by the signature.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

But `Request#shop`, `#topic`, `#webhook_id`, and `#api_version` are all pulled from HTTP headers that are never included in the signed content: [2](#0-1) 

`Registry.process` validates the request purely via `HmacValidator.validate(request)`, which calls `verifiable_query.to_signable_string` (i.e., only the body) and compares it against the HMAC: [3](#0-2) [4](#0-3) 

After signature validation succeeds, the (unauthenticated) `request.shop` value is trusted and passed straight into the handler as the tenant identity: [5](#0-4) 

The identity binding broken is: `hmac_covers(bytes signed) == bytes used to attribute the event to a shop`. In reality `hmac_covers(raw_body) ≠ shop header used for tenant attribution`. Since the same `api_secret_key` is shared by the app across all installs, any unprivileged merchant who has legitimately installed the app on their own store can receive real, validly-signed webhook deliveries (valid HMAC over a given raw body). That merchant can then replay the exact same raw body/HMAC pair to the app's webhook endpoint while substituting the `X-Shopify-Shop-Domain` (and/or `Topic`/`Webhook-Id`) header to claim the event belongs to a different shop. Because the HMAC only signs the body — not the shop or topic headers — `HmacValidator.validate` still returns `true`, and `Registry.process` hands the handler a `WebhookMetadata` claiming an arbitrary `shop` value.

### Impact Explanation
This breaks the shop-authenticated vs. shop-attributed identity binding: the gem gives host applications no assurance that `request.shop` corresponds to the tenant that actually produced the signed body. Any host app that uses `data.shop` from `WebhookMetadata` (as shown in the gem's own documentation) to key per-shop side effects — e.g., processing `app/uninstalled`, `shop/redact`, or `orders/create` — can be tricked by one merchant's replayed/re-headed webhook into performing an action attributed to a different, unrelated shop, i.e., cross-tenant data confusion, without needing the `api_secret_key`, an access token, or any credential belonging to the victim shop.

### Likelihood Explanation
Any unprivileged merchant with a legitimate install of the app can capture their own valid webhook (raw body + `X-Shopify-Hmac-Sha256`) and replay it to the app's public webhook endpoint with a forged `X-Shopify-Shop-Domain`/`X-Shopify-Topic` header. No secrets, tokens, or elevated access are required — only a normal installation and the ability to send an HTTP request, which any internet user with a development store can obtain.

### Recommendation
Bind the tenant-identifying headers into the signed content (or otherwise cryptographically bind `shop`, `topic`, and `webhook_id` to the signature) instead of validating the body alone, and/or require callers to independently verify that `request.shop` matches an existing, actively-installed session before trusting `WebhookMetadata#shop`, making this an explicit, enforced check in `Registry.process` rather than leaving it solely to host-application discipline.

### Proof of Concept
```ruby
# Attacker owns shop "attacker-shop.myshopify.com" with the app legitimately installed.
# They receive a real webhook from Shopify:
raw_body = '{"id":123,"note":"legit order"}'
valid_hmac = OpenSSL::HMAC.digest(OpenSSL::Digest.new("sha256"), Context.api_secret_key, raw_body)

# They replay it against the same endpoint, only changing the shop-domain header:
headers = {
  "x-shopify-topic" => "orders/create",
  "x-shopify-hmac-sha256" => Base64.encode64(valid_hmac),
  "x-shopify-shop-domain" => "victim-shop.myshopify.com", # forged, not covered by HMAC
}

request = ShopifyAPI::Webhooks::Request.new(raw_body: raw_body, headers: headers)
ShopifyAPI::Webhooks::Registry.process(request)
# => HmacValidator.validate(request) returns true (body matches),
#    handler.handle receives WebhookMetadata(shop: "victim-shop.myshopify.com", ...)
```

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
