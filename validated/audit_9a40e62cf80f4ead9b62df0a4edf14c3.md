### Title
Webhook `shop` identity is not covered by the HMAC signature, allowing cross-tenant webhook forgery - ([File: lib/shopify_api/webhooks/request.rb](lib/shopify_api/webhooks/request.rb))

### Summary
`ShopifyAPI::Webhooks::Request` derives the tenant identity (`shop`) from an HTTP header, while the HMAC signature that authenticates the request only covers the raw body. `Registry.process` trusts this unauthenticated header value and hands it directly to the app's webhook handler as the tenant identifier, breaking the binding between "bytes verified by HMAC" and "bytes acted on as the tenant key."

### Finding Description
`Utils::HmacValidator.validate` computes the signature over `verifiable_query.to_signable_string` and compares it to the `hmac` value: [1](#0-0) 

For webhooks, `Request#to_signable_string` returns only `@raw_body` — it never includes the `shop`, `topic`, `webhook_id`, or `api_version` header values: [2](#0-1) 

`Request#shop` is read straight from the `shopify-shop-domain` / `x-shopify-shop-domain` header with no cryptographic binding to the signed body: [3](#0-2) 

`Registry.process` validates the HMAC (over body only) and then forwards `request.shop` verbatim to the app-supplied handler as part of `WebhookMetadata`, which is the documented, trusted way apps identify which tenant a webhook belongs to: [4](#0-3) [5](#0-4) 

**Broken identity binding (equality that should hold but doesn't):**
`shop_used_for_tenant_routing (header, unauthenticated) == shop_that_HMAC_authenticates (not present in signable_string at all)`

The HMAC never binds `shop` to anything — it only proves the request body was produced with the app's secret at some point for *some* shop. It provides zero guarantee about which shop the currently-presented `shop-domain` header corresponds to.

### Impact Explanation
An attacker who legitimately installs the app on their own shop receives real Shopify-signed webhooks (valid `raw_body` + valid `hmac-sha256`) for their own store's data. Because the signature never covers the shop-domain header, the attacker can replay that exact `(raw_body, hmac)` pair directly against the app's public webhook endpoint while substituting an arbitrary `shop-domain` header (e.g., a victim's `myshopify.com` domain). `Registry.process` will pass HMAC validation (body/hmac match) and invoke the app's handler with `WebhookMetadata#shop` set to the attacker-chosen victim shop. Any host application that uses `data.shop` to look up/act on tenant records (the exact pattern this gem documents and expects) will process attacker-controlled data (e.g. order/product/customer payloads) under the victim's tenant identity — a cross-tenant data-injection/confusion vector.

### Likelihood Explanation
High: exploitation requires no secrets beyond having (at least once) legitimately installed the app to obtain a valid `(body, hmac)` pair, and then issuing a normal unauthenticated HTTP POST to the app's public webhook URL with a modified header — well within reach of an unprivileged internet user/merchant. No access token, `client_secret`, or privileged account is required.

### Recommendation
Include the tenant-identifying fields (`shop`, and ideally `topic`, `webhook_id`, `api_version`) in the HMAC-signed string, or otherwise cryptographically bind them to the payload before trusting them for tenant routing — e.g., derive/verify `shop` independently (such as cross-checking against the shop associated with the specific `webhook_id`/subscription via the Admin API) rather than trusting the raw header. At minimum, document loudly that `WebhookMetadata#shop` is *not* authenticated by the HMAC and must not be used as the sole tenant key without additional verification.

### Proof of Concept
1. Attacker installs the app on `attacker.myshopify.com` and lets a webhook (e.g. `orders/create`) fire; captures the exact `raw_body` and the resulting `X-Shopify-Hmac-Sha256` value from the real Shopify-originated POST.
2. Attacker sends a new POST directly to the app's public webhook endpoint with:
   - Body: the exact captured `raw_body`
   - `X-Shopify-Hmac-Sha256`: the exact captured hmac
   - `X-Shopify-Shop-Domain`: `victim-shop.myshopify.com` (arbitrary)
   - `X-Shopify-Topic`: `orders/create`
3. `ShopifyAPI::Webhooks::Request.new` parses the forged headers; `Utils::HmacValidator.validate` recomputes HMAC over `raw_body` only, which matches, so `Registry.process` proceeds: [4](#0-3) 
4. The app's `WebhookHandler#handle` receives `WebhookMetadata(shop: "victim-shop.myshopify.com", body: <attacker's data>, ...)`, causing the attacker's own order/customer data to be attributed to and processed against the victim tenant.

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

**File:** lib/shopify_api/webhooks/request.rb (L10-38)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end

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

**File:** lib/shopify_api/webhooks/webhook_handler.rb (L6-12)
```ruby
    class WebhookMetadata < T::Struct
      const :topic, String
      const :shop, String
      const :body, T::Hash[String, T.untyped]
      const :api_version, String
      const :webhook_id, String
    end
```
