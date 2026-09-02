### Title
Webhook `shop` field is not covered by the HMAC, allowing a replayed valid webhook to be attributed to a different shop - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes the HMAC signature only over the raw request body, while the `shop-domain` header used to identify the tenant that the webhook belongs to is never included in the signed material. `ShopifyAPI::Webhooks::Registry.process` accepts any request whose HMAC matches the body and then hands `request.shop` — taken straight from the unauthenticated header — to the app's `WebhookHandler`. This mirrors the H01 bond-penalty bug class: a field that is acted upon (the shop identity used to route/authorize the webhook) is not bound by the cryptographic check (the HMAC), so the two values can be made to diverge.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Request#shop` is read directly from the `shopify-shop-domain`/`x-shopify-shop-domain` header with no cryptographic linkage to the HMAC: [2](#0-1) 

`HmacValidator.validate` only verifies `verifiable_query.to_signable_string` against the HMAC, i.e., only the body for webhook requests: [3](#0-2) 

`Registry.process` treats a body-only HMAC match as proof the whole request (including `shop`) is trustworthy, then forwards `request.shop` unchanged into `WebhookMetadata` that is delivered to the app's handler: [4](#0-3) [5](#0-4) 

By contrast, the OAuth `AuthQuery` verifiable object correctly binds `shop` (and `host`) into the signed string, so HMAC validation there does cover the tenant-identifying field: [6](#0-5) 

The equality that should hold is: `shop value cryptographically bound by HMAC == shop value the handler acts on`. For webhooks this equality does not hold — the HMAC only proves `secret == HMAC(body)`; it says nothing about which shop the body belongs to.

### Impact Explanation
An attacker who is a legitimate (unprivileged) merchant using the same app can receive a genuinely Shopify-signed webhook for their own store (a normal, unprivileged occurrence — every merchant installing the app gets real webhook deliveries with valid HMACs computed over the body only). Because the HMAC never covers the `shop-domain` header, that same body+HMAC pair remains valid if replayed to the app's webhook endpoint with the `shop-domain` header changed to a victim shop. If the host application trusts `WebhookMetadata#shop` (as the gem's own interface encourages, since it is the only shop indicator supplied to `WebhookHandler#handle`) to select which tenant's session/data to update, this allows cross-tenant data confusion/injection: the attacker's own webhook payload is processed under the identity of a different shop. This matches the "Critical – cross-tenant access" impact bucket in the rules, since the tenant/shop boundary that the HMAC is supposed to establish is not actually enforced for that field.

### Likelihood Explanation
Likelihood is only moderate: exploitation requires the attacker to actually possess a legitimate webhook delivery (achievable by installing the app on their own store and triggering an event) and to know/guess a valid victim shop domain, and it depends on the host app trusting `data.shop` for tenant-sensitive routing without independently cross-checking the shop against its own record of registered webhook endpoints/session store. Many host implementations may already do such cross-checks, but the gem provides no built-in protection and its documented API (`WebhookMetadata`) presents `shop` as if it were verified, which invites misuse.

### Recommendation
Bind the shop identity to the HMAC-verified body, e.g., by requiring the webhook body itself to carry the shop identifier that is checked against the header, or by including the `shop-domain` header in the signable string used for HMAC verification (mirroring how `AuthQuery` binds `shop` and `host`). At minimum, document clearly that `WebhookMetadata#shop` is not cryptographically authenticated and that consuming applications must independently verify it against their own registered shop/session records before trusting it for tenant-scoped operations.

### Proof of Concept
1. App installs on `attacker-shop.myshopify.com`; Shopify sends a legitimate webhook with body `B` and header `x-shopify-hmac-sha256: H`, where `H = HMAC-SHA256(secret, B)`.
2. Attacker captures `B` and `H` (e.g., via their own logging/proxy of their own store's traffic — no privileged access to the app or secret required).
3. Attacker sends a POST to the app's webhook endpoint with the same body `B`, the same header `x-shopify-hmac-sha256: H`, but `x-shopify-shop-domain: victim-shop.myshopify.com`.
4. `ShopifyAPI::Utils::HmacValidator.validate` succeeds because it only checks `HMAC(secret, B) == H`, per [7](#0-6) .
5. `Registry.process` calls the handler with `WebhookMetadata.new(... shop: "victim-shop.myshopify.com", body: parsed_body_of_B ...)`, per [8](#0-7) , causing the attacker-controlled payload to be processed under the victim shop's identity if the host trusts this field.

### Citations

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

**File:** lib/shopify_api/auth/oauth/auth_query.rb (L33-43)
```ruby
        sig { override.returns(String) }
        def to_signable_string
          params = {
            code: code,
            host: host,
            shop: shop,
            state: state,
            timestamp: timestamp,
          }
          URI.encode_www_form(params)
        end
```
