Confirmed: `WebhookMetadata#shop` is the documented tenant-identification field exposed to app handlers [1](#0-0) , but it is sourced from `Request#shop`, an unauthenticated HTTP header [2](#0-1) , while the HMAC only covers `@raw_body` [3](#0-2) .

### Title
Webhook shop identity not covered by HMAC allows cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` verifies webhook authenticity via `Utils::HmacValidator.validate(request)`, but the HMAC signature only binds the raw JSON body, not the `shop` (tenant) identity that is subsequently trusted and handed to the app's webhook handler.

### Finding Description
`ShopifyAPI::Webhooks::Request` implements `Utils::VerifiableQuery` and its `to_signable_string` returns only `@raw_body`: [3](#0-2) 
`HmacValidator.validate` computes the HMAC purely over that signable string and compares it to the `hmac` header: [4](#0-3) [5](#0-4) 
However, `Registry.process` trusts `request.shop` — an unauthenticated header (`shopify-shop-domain`/`x-shopify-shop-domain`) — as the tenant identity and forwards it directly into `WebhookMetadata`, which is the struct the host application's `WebhookHandler#handle` uses to attribute the webhook payload to a shop: [6](#0-5) [2](#0-1) 

The binding that should hold is: `HMAC-verified bytes == bytes the identity ("shop") is derived from`. Here, the signature only proves the body's integrity and that it was HMAC'd with the app's shared secret; it proves nothing about which shop the header claims to be from. Since the API secret is shared by the app across all of its installed shops, a valid HMAC computed for one shop's body is equally valid for the *identical* body sent with a different `shop-domain` header — the signature check cannot detect the substitution because the shop field is entirely outside the signed message.

### Impact Explanation
An attacker who controls (or has installed the app on) one shop can legitimately receive a validly-HMAC'd webhook from Shopify for their own tenant, then replay that exact raw body (with its still-valid HMAC) to the app's webhook endpoint while spoofing the `X-Shopify-Shop-Domain` header to a victim shop. Since `Registry.process` never checks that the shop header is part of the authenticated payload, the forged request passes `Utils::HmacValidator.validate` and is dispatched to the handler tagged with the victim's shop identity. Depending on how the host app models webhook data (e.g., updating orders/customers/inventory keyed by `shop`), this enables cross-tenant data injection or corruption — a merchant can make the app believe attacker-controlled webhook data originated from another merchant's store. This qualifies as cross-tenant access under the Critical impact category.

### Likelihood Explanation
Exploitation requires only that the attacker be a legitimate (even free-tier) installer of the app on their own shop — no privileged account, no leaked secret, and no interaction with `api_secret_key` beyond what's normally exposed through Shopify's own webhook delivery to that attacker's endpoint. Constructing the replayed request (same body/HMAC, different shop header) is a simple HTTP request with attacker-controlled headers, making this straightforward to trigger for anyone with a live installation.

### Recommendation
Include the shop/tenant identity as part of the HMAC-signed message, or cross-verify it independently (e.g., record the shop associated with each webhook registration/subscription id server-side and validate the incoming `shop` header against that mapping, or validate the webhook against Shopify by shop-scoped session rather than trusting the raw header). At minimum, document/require that `shop-domain` from the header must never be trusted for authorization decisions without an additional binding check, since it is fully attacker-controlled and unauthenticated by design in this gem.

### Proof of Concept
1. App installs on `attacker-shop.myshopify.com` and `victim-shop.myshopify.com`, both using the same app (same `api_secret_key`).
2. Shopify sends a legitimate webhook to the attacker's endpoint for `attacker-shop.myshopify.com` with body `B` and header `X-Shopify-Hmac-Sha256: H`, where `H = HMAC-SHA256(secret, B)`.
3. Attacker captures `B` and `H`, then POSTs to the app's webhook endpoint with the same body `B`, same `H` header, but `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Request.new` parses headers/body; `Utils::HmacValidator.validate` recomputes HMAC over `B` only and it matches `H`, so validation passes: [7](#0-6) 
5. `handler.handle` is invoked with `WebhookMetadata#shop == "victim-shop.myshopify.com"` even though the payload was fully attacker-controlled/replayed, causing the app to process attacker data under the victim's tenant identity.

### Citations

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

**File:** lib/shopify_api/webhooks/request.rb (L10-13)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
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
