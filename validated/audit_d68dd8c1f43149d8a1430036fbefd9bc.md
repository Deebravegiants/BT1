### Title
Webhook `shop` (and `topic`/`webhook-id`) headers are trusted for tenant identity but are not covered by the HMAC signature - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw HTTP body, while `shop`, `topic`, and `webhook_id` are read from unauthenticated headers and never included in the signed bytes. `ShopifyAPI::Webhooks::Registry.process` validates the HMAC over the body only, then unconditionally trusts `request.shop` as the tenant identity that is handed to the app's handler.

### Finding Description
`Utils::HmacValidator.validate` computes the expected signature from `verifiable_query.to_signable_string` and compares it to the `hmac` field: [1](#0-0) 

For webhooks, `to_signable_string` is defined as just the raw request body, while `shop`, `topic`, and `webhook_id` are pulled straight from HTTP headers with no cryptographic binding to that body: [2](#0-1) 

`Registry.process` validates the HMAC (over the body only) and then immediately treats `request.shop` as an authenticated fact, forwarding it to the app's handler as the tenant context: [3](#0-2) 

The equality the code implicitly assumes is:
`hmac_valid(raw_body) == authenticated(shop_header)`

But the actual binding is only `hmac_valid(raw_body)`; the `shop-domain` header (along with `topic` and `webhook-id`) is unauthenticated and independently attacker-controlled at the HTTP layer. This is the same bug class as the M-9 analog: a field that is acted upon (`firstBidTime` driving auction duration / here, `shop` driving tenant-scoped handling) is not covered by the binding that is supposed to make it trustworthy (the auction's first-bid state / here, the HMAC signature).

### Impact Explanation
An app that keys any tenant-scoped behavior off `WebhookMetadata#shop` (as the gem's own API encourages — `data.shop` is the field the library hands the developer to identify "which shop this webhook is for") can be made to process a validly-HMAC'd payload under the wrong shop identity. Concretely: a merchant who is themselves a legitimate installed tenant of the app receives real, correctly-signed webhook deliveries from Shopify for their own shop. Because the signature covers only the body, that same `(body, hmac)` pair remains valid no matter what `X-Shopify-Shop-Domain` value is sent alongside it. Replaying the captured body+hmac with a different `shop-domain` header value causes `Registry.process` to pass a spoofed shop identity through as authenticated, to a handler that reasonably treats `data.shop` as tenant-authenticated. Depending on how the host app scopes data per shop from this field, this enables cross-tenant data confusion/write using content the attacker fully controls the interpretation of within their own tenant boundary — a cross-tenant integrity break rooted directly in this gem's HMAC-binding scope (`to_signable_string` in `lib/shopify_api/webhooks/request.rb`).

### Likelihood Explanation
Likelihood is bounded by scope of what an "unprivileged internet user" can obtain: the attacker does not need `api_secret_key` — they only need a legitimately-signed webhook they already receive as a normal (even free/unprivileged) installed merchant of the target app, since Shopify itself signs and delivers it to them. No interception of another tenant's traffic and no possession of the app's `client_secret` is required, only manipulation of the header on a request they can already replay to the app's own public webhook endpoint. This is a realistic, low-privilege exploitation path, though it depends on the host application actually using `data.shop` to scope trust-sensitive actions without independent verification (e.g., cross-checking against a known-installed-shops list) — the gem's documentation does not instruct callers to independently re-validate the header-derived shop, and the gem provides no facility to do so itself.

### Recommendation
Include `shop`, `topic`, and `webhook_id` in the HMAC-signed material (or otherwise cryptographically bind them to the verified body), or explicitly document and enforce that `WebhookMetadata#shop` must never be trusted as authenticated tenant identity and must be cross-checked by the caller against the shop associated with the originally registered webhook subscription before use.

### Proof of Concept
1. App tenant A (attacker, an installed but otherwise unprivileged merchant) receives a legitimate webhook delivery from Shopify: body `B`, header `X-Shopify-Shop-Domain: shop-a.myshopify.com`, and a correctly computed `X-Shopify-Hmac-Sha256: H` (since Shopify signs it with the app's real secret for A's own delivery).
2. Attacker resends the same request to the app's webhook endpoint, keeping body `B` and header `X-Shopify-Hmac-Sha256: H` unchanged, but replacing `X-Shopify-Shop-Domain` with `shop-victim.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` parses headers/body: [4](#0-3) 
4. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes HMAC over `@raw_body` only (`B`) and matches `H` — validation succeeds despite the shop header being forged: [3](#0-2) 
5. The registered handler is invoked with `WebhookMetadata.new(... shop: request.shop ...)` set to `shop-victim.myshopify.com`, an identity that was never authenticated by the HMAC check.

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

**File:** lib/shopify_api/webhooks/request.rb (L15-38)
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

      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end
```

**File:** lib/shopify_api/webhooks/request.rb (L45-63)
```ruby
      sig { params(raw_body: String, headers: T::Hash[String, T.untyped]).void }
      def initialize(raw_body:, headers:)
        # normalize the headers by forcing lowercase, removing any prepended "http"s, and changing underscores to dashes
        headers = headers.to_h { |k, v| [k.to_s.downcase.sub("http_", "").gsub("_", "-"), v] }

        missing_headers = []
        ["topic", "hmac-sha256", "shop-domain"].each do |name|
          unless headers.key?("shopify-#{name}") || headers.key?("x-shopify-#{name}")
            missing_headers << "shopify-#{name} or x-shopify-#{name}"
          end
        end
        unless missing_headers.empty?
          raise Errors::InvalidWebhookError,
            "Missing one or more of the required HTTP headers to process webhooks: #{missing_headers}"
        end

        @headers = headers
        @raw_body = raw_body
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
