### Title
Webhook `shop`, `topic`, and `webhook_id` identifying headers are trusted by handlers without being covered by the HMAC signature, enabling cross-tenant webhook forgery via replay - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` derives the shop, topic, and webhook id purely from unauthenticated HTTP headers, while the HMAC signature that `Registry.process` checks covers only the raw request body. This breaks the binding `shop-that-app-acts-on == shop-that-HMAC-authenticates`, allowing an attacker who legitimately receives one genuinely signed webhook (e.g., by installing the app on their own shop) to replay that body/signature pair with a forged `X-Shopify-Shop-Domain` (and/or topic) header and have it accepted as coming from an arbitrary victim shop.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

but `shop`, `topic`, `api_version`, and `webhook_id` are all read straight from HTTP headers, never included in the signed material: [2](#0-1) 

`Utils::HmacValidator.validate` computes the HMAC exclusively over `verifiable_query.to_signable_string`: [3](#0-2) 

`Registry.process` gates handler invocation solely on this body-only HMAC check, then passes the *unauthenticated* header-derived `shop`/`topic`/`webhook_id` straight into the app's handler: [4](#0-3) 

`WebhookMetadata` treats `shop` as a trusted, authoritative field with no further verification available in the gem: [5](#0-4) 

The equality the gem implicitly promises to callers is: *bytes verified by HMAC == bytes the handler acts on for tenant identity*. In reality: *bytes verified by HMAC (body only) ≠ bytes used to identify the tenant (`shop` header)*. Since the `shop` header is fully attacker-controllable independent of the signed body, any consumer of `WebhookMetadata#shop` for per-tenant lookups/writes is scoping its trust boundary on a header the gem never authenticates.

### Impact Explanation
An attacker who can obtain even one genuinely-signed webhook delivery (trivially achievable by installing the app on a shop they control, or capturing any real webhook body+signature pair for a given topic — since the signature is body-only, it is reusable for any shop as long as the JSON body is identical or crafted to match) can resend that exact body/HMAC pair to the app's webhook endpoint with a forged `X-Shopify-Shop-Domain` header naming a different, victim shop. `Registry.process` validates successfully (the body's HMAC is untouched) and hands the handler a `WebhookMetadata` claiming to be from the victim shop. Any host application that uses `data.shop` to key per-tenant state (e.g., processing `app/uninstalled`, `shop/redact`, `customers/data_request`, inventory/order updates, etc. — the standard and documented usage pattern) can be manipulated into applying attacker-supplied data/state changes under a victim shop's identity. This is a cross-tenant identity confusion rooted in the gem's own webhook verification contract, not in host misuse of an undocumented API — the gem explicitly implements and gates on `Utils::HmacValidator.validate(request)` as "webhook is authentic," yet does not bind that guarantee to the tenant field it hands the caller.

### Likelihood Explanation
Likelihood is moderate-to-high: no `api_secret_key`, access token, or TLS interception is required. The attacker only needs (a) their own installed instance of the target app (any Shopify merchant can install a public app) to receive a legitimately-signed webhook body/HMAC pair, or (b) knowledge of a JSON body whose HMAC they can obtain another way, then (c) network access to POST to the app's public webhook endpoint with a modified `X-Shopify-Shop-Domain` header — an entirely unprivileged action from the internet.

### Recommendation
Bind the tenant-identifying headers into the material that is HMAC-verified, or otherwise cryptographically/authoritatively tie the `shop`, `topic`, and `webhook_id` values to the verified body before constructing `WebhookMetadata`. At minimum, document and/or enforce that `Registry.process` cross-checks the header-derived `shop` against an expected/registered shop (e.g., a shop the app knows it installed for) rather than treating any `shop-domain` header as authoritative whenever the HMAC check passes.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` and triggers a webhook event (e.g., updates a product), receiving a genuine POST from Shopify:
   - Headers: `X-Shopify-Topic: products/update`, `X-Shopify-Shop-Domain: attacker-shop.myshopify.com`, `X-Shopify-Hmac-Sha256: <valid HMAC of body>`
   - Body: `{"id": 123, ...}`
2. Attacker captures this raw body and HMAC value.
3. Attacker resends the identical body and HMAC to the same app's public webhook endpoint, but replaces the header:
   - `X-Shopify-Shop-Domain: victim-shop.myshopify.com`
4. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which only recomputes the HMAC of `@raw_body` — the check passes because the body is untouched: [6](#0-5) 
5. The handler receives `WebhookMetadata.new(topic: "products/update", shop: "victim-shop.myshopify.com", ...)` and, if it uses `data.shop` for tenant-scoped persistence (standard pattern), applies attacker-influenced data under the victim tenant's identity.

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
