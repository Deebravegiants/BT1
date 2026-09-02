### Title
Webhook `shop` identity is not covered by the HMAC, allowing cross-tenant impersonation of webhook events - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` binds a webhook's authenticity only to its raw JSON body via HMAC-SHA256, but the `shop-domain` header — which is passed straight through to the app's `WebhookHandler` as the tenant identifier — is never included in the signed payload. Because the HMAC secret (`Context.api_secret_key`) is the app's single `client_secret`, shared across every merchant that installs the app, a merchant who receives a legitimate, validly-signed webhook for their own shop can replay that exact body/HMAC pair to the app's webhook endpoint while substituting a different `shop-domain` header, and the request will still pass `HmacValidator.validate`.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`HmacValidator.validate` computes the HMAC exclusively over `to_signable_string` and compares it against the `hmac` header: [2](#0-1) 

Meanwhile `Request#shop` is read directly from the `shopify-shop-domain` / `x-shopify-shop-domain` header, entirely outside the signed material: [3](#0-2) 

`Registry.process` validates the HMAC and then forwards `request.shop` — unauthenticated — as the tenant field of `WebhookMetadata` handed to the app's handler: [4](#0-3) [5](#0-4) 

The identity binding that should hold is: `HMAC-verified bytes == bytes used to determine tenant (shop)`. Here it is `HMAC-verified bytes (raw_body) != tenant-selecting bytes (shop header)`. Since the signing secret is the app's shared `client_secret` (not shop-specific), any merchant who has legitimately installed the app and received one authentic webhook can capture that body+HMAC pair and resend it to the app's public webhook endpoint with an arbitrary `x-shopify-shop-domain` value. The signature still validates (the body is unchanged and the secret is the same for all shops), but the app's handler now believes the event originates from a different, victim shop.

### Impact Explanation
Any app logic that uses `WebhookMetadata#shop` to select which merchant's session/data record to act on (e.g., updating order status, redacting customer data, revoking access, writing to a per-shop database row) can be tricked into applying a legitimately-signed payload under a forged tenant identity. This is a cross-tenant data integrity/access issue: a low-privileged existing merchant of the app can inject fabricated webhook events attributed to a different shop, without needing that shop's access token or the app's `client_secret`.

### Likelihood Explanation
Requires the attacker to be a real, unprivileged merchant with the app installed (so they can receive at least one authentic webhook and obtain a valid body/HMAC pair), and requires the target app to trust `WebhookMetadata#shop` for tenant-scoped side effects. No credential theft, TLS interception, or knowledge of `api_secret_key` is needed — only observation of one's own legitimate webhook traffic and a replay to the shared endpoint with a modified header.

### Recommendation
Include the shop domain (and ideally topic/webhook-id) in the material that is cryptographically bound to the request, or otherwise treat `shop-domain` as untrusted unless verified. Since Shopify signs only the body, the gem should document/enforce that consumers must not rely on the `shop` header alone for authorization decisions without corroborating it against a separately verified source (e.g., a per-shop shared secret or session lookup keyed by an authenticated value). At minimum, `Request#shop` should be clearly documented as unauthenticated, and `Registry.process` could optionally require callers to supply an expected/authenticated shop to cross-check against the header before dispatching to the handler.

### Proof of Concept
1. Install the app on `attacker-shop.myshopify.com`; Shopify sends a legitimate webhook with body `B` and header `x-shopify-hmac-sha256: H` (valid for the app's shared `api_secret_key`), plus `x-shopify-shop-domain: attacker-shop.myshopify.com`.
2. Capture `B` and `H`.
3. Send a new HTTP request to the app's webhook endpoint with the same body `B`, same `x-shopify-hmac-sha256: H`, but `x-shopify-shop-domain: victim-shop.myshopify.com`.
4. `ShopifyAPI::Utils::HmacValidator.validate` (via `Registry.process`) passes, because it only checks `B` against `H` using the shared secret: [6](#0-5) 
5. The app's `WebhookHandler#handle` receives `WebhookMetadata` with `shop: "victim-shop.myshopify.com"` and the attacker-controlled body `B`, letting the attacker forge an event apparently from the victim shop.

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
